"""
CLI tool for running job scrapers.
"""
import argparse
import logging
import sys
from pathlib import Path
from typing import List

# Add parent directory to path to enable imports when running as script
PACKAGE_DIR = Path(__file__).parent
if str(PACKAGE_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGE_DIR))

from scrapers import OYKScraper
from utils.config import CAREER_TRACKS
from database import get_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('scraper.log')
    ]
)
logger = logging.getLogger(__name__)


def get_scraper(source: str, headless: bool = True):
    """Get scraper instance by source name."""
    scrapers = {
        'oyk': OYKScraper
    }
    
    scraper_class = scrapers.get(source.lower())
    if not scraper_class:
        raise ValueError(f"Unknown source: {source}. Available: {list(scrapers.keys())}")
    
    return scraper_class(headless=headless)


def scrape_source(source: str, queries: List[str], max_per_query: int = 50, 
                  headless: bool = True) -> int:
    """Scrape a single source for multiple queries."""
    scraper = get_scraper(source, headless)
    total_saved = 0
    
    for query in queries:
        logger.info(f"\n{'='*60}")
        logger.info(f"Scraping {source} for: {query}")
        logger.info('='*60)
        
        try:
            jobs = scraper.scrape(query, max_jobs=max_per_query)
            total_saved += len(jobs)
            logger.info(f"Saved {len(jobs)} jobs for '{query}'")
        except Exception as e:
            logger.error(f"Error scraping {source} for '{query}': {e}")
    
    return total_saved


def scrape_career_track(track: str, max_per_source: int = 50, 
                        headless: bool = True) -> int:
    """Scrape all sources for a specific career track."""
    if track not in CAREER_TRACKS:
        raise ValueError(f"Unknown career track: {track}. Available: {list(CAREER_TRACKS.keys())}")
    
    queries = CAREER_TRACKS[track]
    total_saved = 0
    
    # Only OYK available
    sources = ['oyk']
    
    for source in sources:
        logger.info(f"\n{'#'*60}")
        logger.info(f"Source: {source.upper()}")
        logger.info('#'*60)
        
        saved = scrape_source(source, queries, max_per_query=max_per_source // len(queries), 
                              headless=headless)
        total_saved += saved
    
    return total_saved


def scrape_internships(max_jobs: int = 100, headless: bool = True) -> int:
    """Scrape internships from all sources."""
    total_saved = 0
    
    # OYK has a dedicated internships category
    logger.info("Scraping OYK internships category...")
    oyk_scraper = OYKScraper(headless=headless)
    try:
        jobs = oyk_scraper.scrape_internships(max_jobs=max_jobs)
        total_saved += len(jobs)
    except Exception as e:
        logger.error(f"Error scraping OYK internships: {e}")
    
    return total_saved


def scrape_all(max_per_track: int = 100, headless: bool = True) -> dict:
    """Scrape all career tracks from all sources."""
    results = {}
    
    for track in CAREER_TRACKS:
        logger.info(f"\n{'='*80}")
        logger.info(f"CAREER TRACK: {track.upper().replace('_', ' ')}")
        logger.info('='*80)
        
        saved = scrape_career_track(track, max_per_source=max_per_track, headless=headless)
        results[track] = saved
    
    # Also scrape internships
    logger.info(f"\n{'='*80}")
    logger.info("INTERNSHIPS")
    logger.info('='*80)
    
    results['internships'] = scrape_internships(max_jobs=100, headless=headless)
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description='Kenya Job Market Scraper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_scraper.py --all
  python run_scraper.py --source brightermonday --query "data scientist" --limit 50
  python run_scraper.py --track data_science --limit 100
  python run_scraper.py --internships --limit 50
        """
    )
    
    # Action arguments
    parser.add_argument('--all', action='store_true',
                        help='Scrape all sources for all career tracks')
    parser.add_argument('--source', type=str, 
                        choices=['brightermonday', 'myjobmag', 'oyk'],
                        help='Specific source to scrape')
    parser.add_argument('--track', type=str,
                        choices=list(CAREER_TRACKS.keys()),
                        help='Career track to scrape')
    parser.add_argument('--internships', action='store_true',
                        help='Scrape internships specifically')
    
    # Options
    parser.add_argument('--query', '-q', type=str,
                        help='Custom search query (use with --source)')
    parser.add_argument('--limit', '-l', type=int, default=50,
                        help='Maximum jobs to scrape (default: 50)')
    parser.add_argument('--no-headless', action='store_true',
                        help='Run browser in visible mode (for debugging)')
    parser.add_argument('--stats', action='store_true',
                        help='Show database statistics')
    
    args = parser.parse_args()
    
    headless = not args.no_headless
    
    # Show stats
    if args.stats:
        db = get_db()
        stats = db.get_scrape_stats()
        print("\n📊 Database Statistics:")
        print(f"  Total jobs: {stats['total_jobs']}")
        print(f"  With salary info: {stats['with_salary']}")
        print(f"  Internships: {stats['internships']}")
        print("\n  By Source:")
        for source, count in stats['by_source'].items():
            print(f"    {source}: {count}")
        print("\n  By Career Track:")
        for track, count in stats['by_track'].items():
            print(f"    {track}: {count}")
        return
    
    # Execute scraping based on arguments
    if args.all:
        results = scrape_all(max_per_track=args.limit, headless=headless)
        print("\n📊 Scraping Results:")
        for track, count in results.items():
            print(f"  {track}: {count} jobs saved")
    
    elif args.internships:
        saved = scrape_internships(max_jobs=args.limit, headless=headless)
        print(f"\n✅ Saved {saved} internship postings")
    
    elif args.source and args.query:
        saved = scrape_source(args.source, [args.query], max_per_query=args.limit, 
                              headless=headless)
        print(f"\n✅ Saved {saved} jobs from {args.source}")
    
    elif args.track:
        saved = scrape_career_track(args.track, max_per_source=args.limit, 
                                    headless=headless)
        print(f"\n✅ Saved {saved} jobs for {args.track}")
    
    else:
        parser.print_help()
        print("\n⚠️  Please specify an action: --all, --source, --track, or --internships")


if __name__ == '__main__':
    main()
