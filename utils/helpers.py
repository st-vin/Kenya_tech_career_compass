
import re
import time
import random
from datetime import datetime
from typing import Tuple, Optional

def clean_text(text: str) -> str:
    """Clean and normalize text."""
    if not text:
        return ""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_salary_range(text: str) -> Tuple[Optional[float], Optional[float], str]:
    """Extract salary min, max, and currency from text."""
    if not text:
        return None, None, "KES"
    
    # Simple regex for KES/Ksh salary
    # Look for patterns like "Ksh 50,000 - 80,000" or "50k - 80k"
    
    currency = "KES"
    text_lower = text.lower()
    
    # Check currency
    if "$" in text or "usd" in text_lower:
        currency = "USD"
        
    # Extract numbers
    numbers = re.findall(r'(\d+(?:,\d+)*(?:\.\d+)?)', text)
    if not numbers:
        return None, None, currency
        
    cleaned_nums = [float(n.replace(',', '')) for n in numbers]
    
    if len(cleaned_nums) >= 2:
        return min(cleaned_nums), max(cleaned_nums), currency
    elif len(cleaned_nums) == 1:
        return cleaned_nums[0], None, currency
        
    return None, None, currency

def extract_experience_years(text: str) -> Tuple[Optional[int], Optional[int]]:
    """Extract min and max years of experience."""
    if not text:
        return None, None
        
    # Pattern: "3-5 years" or "3+ years"
    match = re.search(r'(\d+)(?:\s*-\s*(\d+))?\s*(?:years?|yrs?)', text.lower())
    if match:
        min_years = int(match.group(1))
        max_years = int(match.group(2)) if match.group(2) else None
        return min_years, max_years
        
    return None, None

def categorize_career_track(title: str, description: str) -> str:
    """Categorize job into predefined tracks."""
    from utils.config import CAREER_TRACKS
    
    text = (title + " " + description).lower()
    
    for track, keywords in CAREER_TRACKS.items():
        for keyword in keywords:
            if keyword in text:
                return track
                
    return "other"

def is_internship(title: str, description: str) -> bool:
    """Check if job is an internship."""
    text = (title + " " + description).lower()
    return "intern" in text or "trainee" in text or "apprentice" in text

def extract_education_level(text: str) -> str:
    """Extract education level requirement."""
    text_lower = text.lower()
    if "phd" in text_lower or "doctorate" in text_lower:
        return "PhD"
    if "master" in text_lower or "mba" in text_lower or "msc" in text_lower:
        return "Master's"
    if "bachelor" in text_lower or "bsc" in text_lower or "degree" in text_lower:
        return "Bachelor's"
    if "diploma" in text_lower:
        return "Diploma"
    if "certificate" in text_lower:
        return "Certificate"
    return "Not Specified"

def random_delay(min_seconds: float, max_seconds: float):
    """Sleep for a random amount of time."""
    time.sleep(random.uniform(min_seconds, max_seconds))

def normalize_location(location: str) -> str:
    """Normalize location string."""
    if not location:
        return "Unknown"
    
    loc_lower = location.lower()
    if "nairobi" in loc_lower:
        return "Nairobi"
    if "mombasa" in loc_lower:
        return "Mombasa"
    if "remote" in loc_lower:
        return "Remote"
        
    return clean_text(location).title()

def parse_date(date_str: str) -> Optional[datetime]:
    """Parse various date formats."""
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        pass
    # Add more formats as needed
    return datetime.utcnow() # Fallback
