# Scrapers package
from scrapers.base_scraper import BaseScraper
from scrapers.brightermonday import BrighterMondayScraper
from scrapers.myjobmag import MyJobMagScraper
from scrapers.oyk import OYKScraper

__all__ = [
    'BaseScraper',
    'BrighterMondayScraper',
    'MyJobMagScraper', 
    'OYKScraper'
]
