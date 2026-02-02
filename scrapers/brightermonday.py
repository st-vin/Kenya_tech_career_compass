"""
BrighterMonday Kenya scraper.
"""
import logging
from typing import List, Dict, Optional, Any
from urllib.parse import urlencode, urljoin

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from scrapers.base_scraper import BaseScraper
from utils.helpers import parse_date

logger = logging.getLogger(__name__)


class BrighterMondayScraper(BaseScraper):
    """Scraper for BrighterMonday Kenya job listings."""
    
    def __init__(self, headless: bool = True):
        super().__init__(headless)
        self.source_name = "brightermonday"
        self.base_url = "https://www.brightermonday.co.ke"
    
    def build_search_url(self, query: str, page: int = 1) -> str:
        """Build BrighterMonday search URL."""
        params = {
            'q': query
        }
        if page > 1:
            params['page'] = page
        
        return f"{self.base_url}/jobs?{urlencode(params)}"
    
    def parse_job_listing(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Parse job listings from search results page."""
        jobs = []
        
        # BrighterMonday job cards
        job_cards = soup.select('article.mx-5, div.search-result, div[class*="JobCard"]')
        
        # Alternative selectors
        if not job_cards:
            job_cards = soup.select('div.job-card, div[data-testid="job-card"], a[href*="/jobs/"]')
        
        logger.info(f"Found {len(job_cards)} job cards")
        
        for card in job_cards:
            try:
                job = {}
                
                # Title and URL
                title_elem = card.select_one('h3 a, h2 a, a[class*="title"], .job-title a')
                if title_elem:
                    job['title'] = title_elem.get_text(strip=True)
                    href = title_elem.get('href', '')
                    job['url'] = urljoin(self.base_url, href) if href else ''
                else:
                    # Try to get URL from card link
                    link = card.select_one('a[href*="/jobs/"]')
                    if link:
                        job['url'] = urljoin(self.base_url, link.get('href', ''))
                        job['title'] = link.get_text(strip=True) or card.get_text(strip=True)[:100]
                
                if not job.get('url'):
                    continue
                
                # Company
                company_elem = card.select_one('.company-name, span[class*="company"], div[class*="company"]')
                if company_elem:
                    job['company'] = company_elem.get_text(strip=True)
                
                # Location
                location_elem = card.select_one('.location, span[class*="location"], div[class*="location"]')
                if location_elem:
                    job['location'] = location_elem.get_text(strip=True)
                
                # Salary (BrighterMonday often shows salary)
                salary_elem = card.select_one('.salary, span[class*="salary"], div[class*="salary"]')
                if salary_elem:
                    job['salary_text'] = salary_elem.get_text(strip=True)
                
                # Date posted
                date_elem = card.select_one('.date, time, span[class*="date"], span[class*="posted"]')
                if date_elem:
                    date_text = date_elem.get('datetime') or date_elem.get_text(strip=True)
                    job['date_posted'] = parse_date(date_text)
                
                jobs.append(job)
                
            except Exception as e:
                logger.debug(f"Error parsing job card: {e}")
                continue
        
        return jobs
    
    def parse_job_details(self, url: str) -> Optional[Dict[str, Any]]:
        """Parse detailed job information from job page."""
        soup = self.get_page(url)
        if not soup:
            return None
        
        details = {}
        
        try:
            # Job description
            desc_elem = soup.select_one('.job-description, div[class*="description"], article')
            if desc_elem:
                details['description'] = desc_elem.get_text(separator=' ', strip=True)
            
            # Experience
            exp_elem = soup.select_one('span[class*="experience"], div[class*="experience"]')
            if exp_elem:
                details['experience_text'] = exp_elem.get_text(strip=True)
            
            # Look for experience in description
            if not details.get('experience_text') and details.get('description'):
                desc_lower = details['description'].lower()
                if 'experience' in desc_lower:
                    # Try to extract experience from description
                    import re
                    exp_match = re.search(r'\d+\+?\s*(?:years?|yrs?)\s*(?:of\s+)?experience', desc_lower)
                    if exp_match:
                        details['experience_text'] = exp_match.group()
            
            # Job type
            job_type_elem = soup.select_one('span[class*="job-type"], span[class*="employment"]')
            if job_type_elem:
                details['job_type'] = job_type_elem.get_text(strip=True)
            
            # Salary (more detailed on job page)
            salary_elem = soup.select_one('.salary-range, div[class*="salary"], span[class*="salary"]')
            if salary_elem:
                details['salary_text'] = salary_elem.get_text(strip=True)
            
            # Company if not already found
            company_elem = soup.select_one('.company-name, h2[class*="company"], a[class*="company"]')
            if company_elem:
                details['company'] = company_elem.get_text(strip=True)
            
            # Location
            location_elem = soup.select_one('.job-location, span[class*="location"]')
            if location_elem:
                details['location'] = location_elem.get_text(strip=True)
            
        except Exception as e:
            logger.error(f"Error parsing job details: {e}")
        
        return details


# Factory function for convenience
def create_scraper(headless: bool = True) -> BrighterMondayScraper:
    return BrighterMondayScraper(headless=headless)
