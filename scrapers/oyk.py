"""
Opportunities for Young Kenyans (OYK) scraper.
Blog-based site with job postings as WordPress posts.
"""
import logging
from typing import List, Dict, Optional, Any
from urllib.parse import urlencode, urljoin
import re

from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper
from utils.helpers import parse_date

logger = logging.getLogger(__name__)


class OYKScraper(BaseScraper):
    """Scraper for OpportunitiesForYoungKenyans.co.ke job listings."""
    
    def __init__(self, headless: bool = True):
        super().__init__(headless)
        self.source_name = "oyk"
        self.base_url = "https://opportunitiesforyoungkenyans.co.ke"
    
    def build_search_url(self, query: str, page: int = 1) -> str:
        """Build OYK search URL (WordPress search)."""
        params = {
            's': query
        }
        if page > 1:
            params['paged'] = page
        
        return f"{self.base_url}/?{urlencode(params)}"
    
    def build_category_url(self, category: str = "internship", page: int = 1) -> str:
        """Build category URL for browsing by category."""
        # Common categories on OYK
        category_map = {
            'internship': 'internships',
            'job': 'jobs',
            'scholarship': 'scholarships',
            'graduate': 'graduate-programs'
        }
        
        cat = category_map.get(category.lower(), category)
        if page > 1:
            return f"{self.base_url}/category/{cat}/page/{page}/"
        return f"{self.base_url}/category/{cat}/"
    
    def parse_job_listing(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Parse job listings from search/category results page."""
        jobs = []
        
        # OYK uses WordPress with article tags
        articles = soup.select('article, div.post, div.entry, li.post-item')
        
        # Alternative: look for post links
        if not articles:
            articles = soup.select('a[href*="/202"]')  # Posts typically have year in URL
        
        logger.info(f"Found {len(articles)} article cards")
        
        for article in articles:
            try:
                job = {}
                
                # Title and URL
                title_elem = article.select_one('h2.entry-title a, h3 a, a.entry-title, .post-title a')
                if title_elem:
                    job['title'] = title_elem.get_text(strip=True)
                    href = title_elem.get('href', '')
                    job['url'] = href if href.startswith('http') else urljoin(self.base_url, href)
                elif article.name == 'a':
                    job['url'] = article.get('href', '')
                    job['title'] = article.get_text(strip=True)
                
                if not job.get('url') or not job.get('title'):
                    continue
                
                # Filter out non-job posts
                title_lower = job['title'].lower()
                if any(skip in title_lower for skip in ['gallery', 'video', 'news update']):
                    continue
                
                # Extract company from title (OYK format: "Company Hiring Position")
                title = job['title']
                if ' hiring ' in title.lower():
                    parts = title.lower().split(' hiring ')
                    if len(parts) >= 2:
                        job['company'] = parts[0].strip().title()
                elif ' open at ' in title.lower():
                    match = re.search(r'open at (.+?)$', title, re.I)
                    if match:
                        job['company'] = match.group(1).strip()
                
                # Date posted
                date_elem = article.select_one('time, .entry-date, span.date, .post-date')
                if date_elem:
                    date_text = date_elem.get('datetime') or date_elem.get_text(strip=True)
                    job['date_posted'] = parse_date(date_text)
                
                # Check for internship in title
                if 'internship' in title_lower or 'intern' in title_lower:
                    job['is_internship_hint'] = True
                
                jobs.append(job)
                
            except Exception as e:
                logger.debug(f"Error parsing article: {e}")
                continue
        
        return jobs
    
    def parse_job_details(self, url: str) -> Optional[Dict[str, Any]]:
        """Parse detailed job information from post page."""
        soup = self.get_page(url)
        if not soup:
            return None
        
        details = {}
        
        try:
            # Post content
            content_elem = soup.select_one('article .entry-content, div.post-content, .single-content')
            if content_elem:
                details['description'] = content_elem.get_text(separator=' ', strip=True)
            
            # Try to extract location (often mentioned in post)
            if details.get('description'):
                desc_lower = details['description'].lower()
                
                # Common Kenya locations
                locations = ['nairobi', 'mombasa', 'kisumu', 'nakuru', 'eldoret', 'kenya']
                for loc in locations:
                    if loc in desc_lower:
                        details['location'] = loc.title()
                        break
                
                # Experience extraction
                exp_pattern = r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s+)?experience'
                exp_match = re.search(exp_pattern, desc_lower)
                if exp_match:
                    details['experience_text'] = exp_match.group()
                
                # Check for deadline
                deadline_pattern = r'deadline[:\s]+([A-Za-z]+ \d{1,2},? \d{4})'
                deadline_match = re.search(deadline_pattern, desc_lower, re.I)
                if deadline_match:
                    details['deadline_text'] = deadline_match.group(1)
            
            # Try to find company in the post
            company_elem = soup.select_one('.company, strong:first-of-type')
            if company_elem and not details.get('company'):
                # OYK often bolds the company name
                text = company_elem.get_text(strip=True)
                if len(text) < 100:  # Likely a company name, not a paragraph
                    details['company'] = text
            
        except Exception as e:
            logger.error(f"Error parsing job details: {e}")
        
        return details
    
    def scrape_internships(self, max_jobs: int = 50) -> List[Dict[str, Any]]:
        """Scrape specifically from internships category."""
        self.start_driver()
        
        log_id = self.db.start_scrape_log(self.source_name, "internships")
        jobs_found = 0
        jobs_saved = 0
        errors = 0
        saved_jobs = []
        
        try:
            page = 1
            while jobs_found < max_jobs:
                url = self.build_category_url('internship', page)
                logger.info(f"Scraping internships page {page}: {url}")
                
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
                        # Get detailed info
                        if listing.get('url'):
                            details = self.parse_job_details(listing['url'])
                            if details:
                                listing.update(details)
                        
                        # Mark as internship
                        listing['is_internship'] = True
                        
                        # Process and save
                        processed = self.process_job_data(listing)
                        skills = self.extract_skills_from_text(
                            processed.get('description', '')
                        )
                        
                        if self.save_job(processed, skills):
                            jobs_saved += 1
                            saved_jobs.append(processed)
                            
                    except Exception as e:
                        logger.error(f"Error processing job: {e}")
                        errors += 1
                
                page += 1
                
            self.db.update_scrape_log(
                log_id,
                jobs_found=jobs_found,
                jobs_saved=jobs_saved,
                errors=errors,
                status='completed'
            )
            
            logger.info(f"Internship scraping completed: {jobs_found} found, {jobs_saved} saved")
            
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            self.db.update_scrape_log(
                log_id,
                status='failed',
                error_message=str(e)
            )
        
        finally:
            self.stop_driver()
        
        return saved_jobs


def create_scraper(headless: bool = True) -> OYKScraper:
    return OYKScraper(headless=headless)
