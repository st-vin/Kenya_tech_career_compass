
import re
from typing import List, Dict, Optional

class NLPProcessor:
    """Simplified NLP Processor for extracting entities without heavy dependencies."""
    
    def __init__(self):
        pass
        
    def extract_location(self, text: str) -> Optional[str]:
        """Simple rule-based location extraction."""
        locations = ["Nairobi", "Mombasa", "Kisumu", "Remote", "Kenya"]
        text_lower = text.lower()
        for loc in locations:
            if loc.lower() in text_lower:
                return loc
        return None
        
    def extract_company(self, text: str) -> Optional[str]:
        """Simple company extraction (heuristics)."""
        # Very hard to do reliably without NER model, returning None to be safe or simple heuristics
        return None
        
    def extract_salary(self, text: str) -> Optional[str]:
        """Extract salary text snippet."""
        match = re.search(r'(?:ush|kes|ksh\.?|shs)[\s\d,\.]+(?:\s*-\s*[\d,\.]+)?', text, re.IGNORECASE)
        if match:
            return match.group(0)
        return None
        
    def categorize_by_similarity(self, text: str, categories: Dict[str, str]) -> str:
        """Categorize text based on keyword overlap."""
        text_lower = text.lower()
        best_cat = "other"
        max_score = 0
        
        for cat, keywords_str in categories.items():
            keywords = keywords_str.lower().split()
            score = sum(1 for k in keywords if k in text_lower)
            if score > max_score:
                max_score = score
                best_cat = cat
                
        return best_cat

    def extract_education(self, text: str) -> List[str]:
        """Extract education requirements."""
        edu = []
        text_lower = text.lower()
        if "degree" in text_lower or "bachelor" in text_lower:
            edu.append("Degree")
        if "master" in text_lower:
            edu.append("Masters")
        return edu
