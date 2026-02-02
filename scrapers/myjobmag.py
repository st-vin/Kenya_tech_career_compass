"""
MyJobMag Kenya scraper.
"""
import logging
from typing import List, Dict, Optional, Any
from urllib.parse import urlencode, urljoin

from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper
from utils.helpers import parse_date

logger = logging.getLogger(__name__)


class MyJobMagScraper(BaseScraper):
    """Scraper for MyJobMag Kenya job listings."""
    
    def __init__(self, headless: bool = True):
        super().__init__(headless)
        self.source_name = "myjobmag"
        self.base_url = "https://www.myjobmag.co.ke"
    
    def build_search_url(self, query: str, page: int = 1) -> str:
        """Build MyJobMag search URL."""
        # MyJobMag uses a different URL format
        query_slug = query.replace(' ', '-').lower()
        
        if page > 1:
            return f"{self.base_url}/jobs/search/{query_slug}?page={page}"
        return f"{self.base_url}/jobs/search/{query_slug}"
    
    def parse_job_listing(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Parse job listings from search results page."""
        jobs = []
        
        # MyJobMag job cards
        job_cards = soup.select('div.job-list-item, article.job-item, div.mag-b, li.job-item')
        
        # Alternative selectors
        if not job_cards:
            job_cards = soup.select('div[class*="job"], a.job-title-link')
        
        logger.info(f"Found {len(job_cards)} job cards")
        
        for card in job_cards:
            try:
                job = {}
                
                # Title and URL
                title_elem = card.select_one('a.job-title, h2 a, a[class*="title"], .job-title a')
                if title_elem:
                    job['title'] = title_elem.get_text(strip=True)
                    href = title_elem.get('href', '')
                    job['url'] = urljoin(self.base_url, href) if href else ''
                else:
                    link = card.select_one('a[href*="/job/"]')
                    if link:
                        job['url'] = urljoin(self.base_url, link.get('href', ''))
                        job['title'] = card.select_one('h2, h3, .title')
                        job['title'] = job['title'].get_text(strip=True) if job['title'] else ''
                
                if not job.get('url'):
                    continue
                
                # Company
                company_elem = card.select_one('.company-name, .job-company, span.company, a[class*="company"]')
                if company_elem:
                    job['company'] = company_elem.get_text(strip=True)
                
                # Location
                location_elem = card.select_one('.location, .job-location, span[class*="location"]')
                if location_elem:
                    job['location'] = location_elem.get_text(strip=True)
                
                # Experience (MyJobMag often shows experience instead of salary)
                exp_elem = card.select_one('.experience, span[class*="experience"], .job-exp')
                if exp_elem:
                    job['experience_text'] = exp_elem.get_text(strip=True)
                
                # Date posted
                date_elem = card.select_one('.date, time, .posted-date, span[class*="date"]')
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
            desc_elem = soup.select_one('.job-description, .description, article.job-content')
            if desc_elem:
                details['description'] = desc_elem.get_text(separator=' ', strip=True)
            
            # Requirements section
            req_elem = soup.select_one('.job-requirements, .requirements, div[class*="requirement"]')
            if req_elem:
                req_text = req_elem.get_text(separator=' ', strip=True)
                details['description'] = f"{details.get('description', '')} {req_text}"
            
            # Experience
            exp_elem = soup.select_one('span.experience, .job-experience, div[class*="experience"]')
            if exp_elem:
                details['experience_text'] = exp_elem.get_text(strip=True)
            
            # Job type
            job_type_elem = soup.select_one('.job-type, .employment-type, span[class*="type"]')
            if job_type_elem:
                details['job_type'] = job_type_elem.get_text(strip=True)
            
            # Company
            company_elem = soup.select_one('.company-name, h2.company, .job-company')
            if company_elem:
                details['company'] = company_elem.get_text(strip=True)
            
            # Location
            location_elem = soup.select_one('.job-location, .location, span[class*="location"]')
            if location_elem:
                details['location'] = location_elem.get_text(strip=True)
            
        except Exception as e:
            logger.error(f"Error parsing job details: {e}")
        
        return details


def create_scraper(headless: bool = True) -> MyJobMagScraper:
    return MyJobMagScraper(headless=headless)
