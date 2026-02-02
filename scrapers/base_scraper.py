"""
Base scraper class with common functionality for all job site scrapers.
"""
import time
import random
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, 
    WebDriverException, StaleElementReferenceException
)
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

from utils.config import SCRAPE_CONFIG, HARD_SKILLS, SOFT_SKILLS
from utils.helpers import (
    clean_text, extract_salary_range, extract_experience_years,
    categorize_career_track, is_internship, extract_education_level,
    random_delay, normalize_location
)
from database import get_db, Job, Skill
from utils.nlp_processor import NLPProcessor
from utils.config import CAREER_TRACKS

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Abstract base class for job site scrapers."""
    
    def __init__(self, headless: bool = True):
        """Initialize the scraper with a Chrome WebDriver."""
        self.headless = headless
        self.driver = None
        self.db = get_db()
        self.source_name = "base"  # Override in subclasses
        self.nlp = NLPProcessor()
        
    def start_driver(self):
        """Initialize Chrome WebDriver."""
        if self.driver:
            return
            
        options = Options()
        
        if self.headless:
            options.add_argument('--headless=new')
        
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument(f'--user-agent={SCRAPE_CONFIG["user_agent"]}')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.implicitly_wait(10)
            logger.info(f"Chrome WebDriver started for {self.source_name}")
        except Exception as e:
            logger.error(f"Failed to start WebDriver: {e}")
            raise
    
    def stop_driver(self):
        """Close the WebDriver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.info(f"WebDriver closed for {self.source_name}")
    
    def get_page(self, url: str, wait_for: str = None) -> Optional[BeautifulSoup]:
        """
        Navigate to URL and return BeautifulSoup object.
        Optionally wait for an element to be present.
        """
        try:
            self.driver.get(url)
            random_delay(SCRAPE_CONFIG['delay_min'], SCRAPE_CONFIG['delay_max'])
            
            if wait_for:
                WebDriverWait(self.driver, SCRAPE_CONFIG['timeout']).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, wait_for))
                )
            
            return BeautifulSoup(self.driver.page_source, 'lxml')
            
        except TimeoutException:
            logger.warning(f"Timeout waiting for page: {url}")
            return None
        except WebDriverException as e:
            logger.error(f"WebDriver error loading {url}: {e}")
            return None
    
    def extract_skills_from_text(self, text: str) -> List[Dict[str, str]]:
        """Extract skills from job description text."""
        if not text:
            return []
        
        text_lower = text.lower()
        skills = []
        seen = set()
        
        # Check hard skills
        for category, skill_list in HARD_SKILLS.items():
            for skill in skill_list:
                if skill.lower() in text_lower and skill.lower() not in seen:
                    skills.append({
                        'skill_name': skill,
                        'skill_category': category
                    })
                    seen.add(skill.lower())
        
        # Check soft skills
        for skill in SOFT_SKILLS:
            if skill.lower() in text_lower and skill.lower() not in seen:
                skills.append({
                    'skill_name': skill,
                    'skill_category': 'soft_skill'
                })
                seen.add(skill.lower())
        
        return skills
    
    def process_job_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw job data into standardized format."""
        title = raw_data.get('title', '')
        description = raw_data.get('description', '')
        
        # Extract salary
        salary_text = raw_data.get('salary_text', '')
        salary_min, salary_max, currency = extract_salary_range(salary_text)
        
        # Extract experience
        exp_text = raw_data.get('experience_text', description)
        exp_min, exp_max = extract_experience_years(exp_text)
        
        # Categorize
        career_track = categorize_career_track(title, description)
        is_intern = is_internship(title, description)
        education = extract_education_level(description)
        location = normalize_location(raw_data.get('location', ''))
        
        # NLP Augmentation
        if not title:
            # Maybe title is embedded in description?
            # For now just keep empty, but could use NLP to find "Job Title: ..."
            pass
            
        location = normalize_location(raw_data.get('location', ''))
        if location in ["Unknown", "Kenya", ""] and description:
            extracted_loc = self.nlp.extract_location(description)
            if extracted_loc:
                location = normalize_location(extracted_loc)
                
        company = clean_text(raw_data.get('company', ''))
        if not company and description:
            extracted_comp = self.nlp.extract_company(description)
            if extracted_comp:
                company = clean_text(extracted_comp)

        # Salary Augmentation
        if not salary_min and not salary_max:
            extracted_salary = self.nlp.extract_salary(description)
            if extracted_salary:
                # Try to parse the extracted salary text
                s_min, s_max, s_curr = extract_salary_range(extracted_salary)
                if s_min or s_max:
                    salary_min, salary_max, currency = s_min, s_max, s_curr
                    salary_text = extracted_salary

        # Track categorization
        if career_track == "other":
            # Try NLP similarity if keyword match failed
            # Flatten keywords for similarity check or use category names
            track_categories = {track: " ".join(keywords) for track, keywords in CAREER_TRACKS.items()}
            full_text = f"{title} {description}"
            career_track = self.nlp.categorize_by_similarity(full_text, track_categories)

        return {
            'title': clean_text(title),
            'company': company,
            'location': location,
            'description': clean_text(description),
            'salary_min': salary_min,
            'salary_max': salary_max,
            'salary_currency': currency,
            'salary_text': salary_text,
            'experience_years_min': exp_min,
            'experience_years_max': exp_max,
            'experience_text': raw_data.get('experience_text', ''),
            'career_track': career_track,
            'job_type': raw_data.get('job_type', ''),
            'is_internship': is_intern,
            'education_level': education,
            'source': self.source_name,
            'url': raw_data.get('url', ''),
            'date_posted': raw_data.get('date_posted'),
            'date_scraped': datetime.utcnow()
        }
    
    
    def extract_requirements(self, text: str) -> List[Dict[str, str]]:
        """Extract requirements like education from text."""
        reqs = []
        
        # Education using NLP
        edu_list = self.nlp.extract_education(text)
        for edu in edu_list:
            reqs.append({
                'requirement_type': 'education',
                'requirement_value': edu,
                'is_required': True
            })
            
        return reqs

    def save_job(self, job_data: Dict[str, Any], skills: List[Dict] = None, 
                 requirements: List[Dict] = None) -> bool:
        """Save a job to the database."""
        try:
            # Check if URL already exists
            if self.db.get_job_by_url(job_data.get('url')):
                logger.debug(f"Job already exists: {job_data.get('url')}")
                return False
            
            job = self.db.add_job(job_data, skills=skills, requirements=requirements)
            if job:
                logger.info(f"Saved job: {job_data.get('title', '')[:50]}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error saving job: {e}")
            return False
    
    @abstractmethod
    def build_search_url(self, query: str, page: int = 1) -> str:
        """Build search URL for the job site. Override in subclasses."""
        pass
    
    @abstractmethod
    def parse_job_listing(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Parse job listings from search results page. Override in subclasses."""
        pass
    
    @abstractmethod
    def parse_job_details(self, url: str) -> Optional[Dict[str, Any]]:
        """Parse detailed job information from job page. Override in subclasses."""
        pass
    
    def scrape(self, query: str, max_jobs: int = 50, 
               scrape_details: bool = True) -> List[Dict[str, Any]]:
        """
        Main scraping method.
        
        Args:
            query: Search query
            max_jobs: Maximum number of jobs to scrape
            scrape_details: Whether to visit individual job pages
            
        Returns:
            List of scraped and saved jobs
        """
        self.start_driver()
        
        log_id = self.db.start_scrape_log(self.source_name, query)
        jobs_found = 0
        jobs_saved = 0
        errors = 0
        saved_jobs = []
        
        try:
            page = 1
            while jobs_found < max_jobs:
                url = self.build_search_url(query, page)
                logger.info(f"Scraping page {page}: {url}")
                
                soup = self.get_page(url)
                if not soup:
                    errors += 1
                    break
                
                listings = self.parse_job_listing(soup)
                if not listings:
                    logger.info("No more listings found")
                    break
                
                for listing in listings:
                    if jobs_found >= max_jobs:
                        break
                    
                    jobs_found += 1
                    
                    try:
                        # Get detailed info if needed
                        if scrape_details and listing.get('url'):
                            details = self.parse_job_details(listing['url'])
                            if details:
                                listing.update(details)
                        
                        # Process and save
                        processed = self.process_job_data(listing)
                        skills = self.extract_skills_from_text(
                            processed.get('description', '')
                        )
                        requirements = self.extract_requirements(
                            processed.get('description', '')
                        )
                        
                        if self.save_job(processed, skills, requirements):
                            jobs_saved += 1
                            saved_jobs.append(processed)
                            
                    except Exception as e:
                        logger.error(f"Error processing job: {e}")
                        errors += 1
                
                page += 1
                random_delay(3, 6)  # Longer delay between pages
            
            self.db.update_scrape_log(
                log_id, 
                jobs_found=jobs_found,
                jobs_saved=jobs_saved,
                errors=errors,
                status='completed'
            )
            
            logger.info(f"Scraping completed: {jobs_found} found, {jobs_saved} saved, {errors} errors")
            
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            self.db.update_scrape_log(
                log_id,
                jobs_found=jobs_found,
                jobs_saved=jobs_saved,
                errors=errors,
                status='failed',
                error_message=str(e)
            )
        
        finally:
            self.stop_driver()
        
        return saved_jobs
