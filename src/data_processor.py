"""
Data processor for cleaning and normalizing Kenya tech job data.
Uses "Hiring" pattern extraction for company names.
"""
import pandas as pd
import re
from pathlib import Path


# Known company name mappings (lowercase -> canonical)
COMPANY_MAPPINGS = {
    "co-operative bank": "Co-operative Bank of Kenya",
    "coop bank": "Co-operative Bank of Kenya",
    "cooperative bank": "Co-operative Bank of Kenya",
    "equity bank": "Equity Bank Kenya",
    "absa bank": "Absa Bank Kenya",
    "absa": "Absa Bank Kenya",
    "kcb bank": "KCB Bank Kenya",
    "kcb": "KCB Bank Kenya",
    "k.c.b": "KCB Bank Kenya",
    "cbk": "Central Bank of Kenya",
    "central bank": "Central Bank of Kenya",
    "safaricom": "Safaricom PLC",
    "cifor-icraf": "CIFOR-ICRAF",
    "cifor": "CIFOR-ICRAF",
    "icraf": "CIFOR-ICRAF",
    "world agroforestry": "CIFOR-ICRAF",
    "tatu city": "Tatu City",
    "strathmore": "Strathmore University",
    "strathmore university": "Strathmore University",
    "kwal": "KWAL",
    "soledad": "Soledad",
    "ncba": "NCBA Bank",
    "ncba bank": "NCBA Bank",
    "standard chartered": "Standard Chartered Bank",
    "stanchart": "Standard Chartered Bank",
    "dtb": "Diamond Trust Bank",
    "diamond trust": "Diamond Trust Bank",
    "i&m bank": "I&M Bank",
    "i&m": "I&M Bank",
    "family bank": "Family Bank",
    "sidian bank": "Sidian Bank",
    "gtbank": "GTBank Kenya",
    "gt bank": "GTBank Kenya",
    "stanbic": "Stanbic Bank",
    "stanbic bank": "Stanbic Bank",
    "jubilee insurance": "Jubilee Insurance",
    "jubilee": "Jubilee Insurance",
    "britam": "Britam",
    "britam insurance": "Britam",
    "icea lion": "ICEA Lion",
    "mtn": "MTN",
    "airtel": "Airtel Kenya",
    "telkom": "Telkom Kenya",
    "un-habitat": "UN-Habitat",
    "un habitat": "UN-Habitat",
    "unep": "UNEP",
    "undp": "UNDP",
    "unicef": "UNICEF",
    "world bank": "World Bank",
    "microsoft": "Microsoft",
    "google": "Google",
    "meta": "Meta",
    "amazon": "Amazon",
    "ibm": "IBM",
}

# Valid Kenyan cities
VALID_CITIES = ["nairobi", "mombasa", "kisumu", "eldoret", "nakuru", "thika"]


def extract_company_from_title(title: str) -> tuple[str, str]:
    """
    Extract company name from job title using "Hiring" pattern.
    Returns (company_name, job_title).
    
    Pattern: [COMPANY] Hiring [JOB TITLE]
    """
    if pd.isna(title) or not title.strip():
        return "Unknown", ""
    
    title = title.strip()
    
    # Primary pattern: Split on "Hiring" (case-insensitive)
    # Use non-greedy match to get first occurrence
    pattern = re.compile(r"^(.+?)\s+hiring\s+(.+)$", re.IGNORECASE)
    match = pattern.match(title)
    
    if match:
        company_raw = match.group(1).strip()
        job_title = match.group(2).strip()
        
        # Validate company name
        if len(company_raw) >= 2 and any(c.isalpha() for c in company_raw):
            # Normalize to canonical name if in lookup
            company_clean = normalize_company_name(company_raw)
            return company_clean, job_title
    
    # Fallback pattern: Check for " - " separator (e.g., "Data Scientist - Equity Bank")
    if " - " in title:
        parts = title.split(" - ")
        for part in parts:
            company_clean = normalize_company_name(part.strip())
            if company_clean != part.strip():  # Found in lookup
                # The other part is likely the job title
                job_title = " - ".join(p for p in parts if p.strip() != part.strip())
                return company_clean, job_title
    
    # Fallback: Check if any known company appears in the title
    title_lower = title.lower()
    for pattern_key, canonical in COMPANY_MAPPINGS.items():
        if pattern_key in title_lower:
            # Extract company and infer job title
            return canonical, title  # Keep full title as job title for now
    
    # No pattern matched
    return "Unknown", title


def normalize_company_name(company_raw: str) -> str:
    """
    Normalize company name using lookup table.
    """
    if pd.isna(company_raw) or not company_raw.strip():
        return "Unknown"
    
    company_lower = company_raw.strip().lower()
    
    # Check against known mappings
    for pattern, canonical in COMPANY_MAPPINGS.items():
        if pattern in company_lower or company_lower in pattern:
            return canonical
    
    # Return cleaned version (title case)
    return company_raw.strip().title()


def normalize_location(location: str) -> str:
    """
    Normalize location to standard format.
    - Valid cities: Nairobi, Mombasa, Kisumu, Eldoret
    - Remote/Hybrid: Keep as-is
    - Invalid/missing: Default to Nairobi
    """
    if pd.isna(location) or not location.strip():
        return "Nairobi"
    
    loc_lower = location.strip().lower()
    
    # Check for remote/hybrid
    if "remote" in loc_lower:
        return "Remote"
    if "hybrid" in loc_lower:
        return "Hybrid"
    
    # Check for valid cities
    for city in VALID_CITIES:
        if city in loc_lower:
            return city.title()
    
    # Invalid location (e.g., "Tableau", "Bi") -> default to Nairobi
    return "Nairobi"


def classify_domain(title: str, career_track: str = "") -> str:
    """
    Classify job into domain based on title and career_track.
    """
    # Use career_track if available and valid
    if career_track and career_track in ["data_science", "web_dev", "cyber_security"]:
        return career_track
    
    if pd.isna(title):
        return "other"
    
    title_lower = title.lower()
    
    # Data Science keywords
    ds_keywords = [
        "data scientist", "data analyst", "machine learning", "ml engineer",
        "data engineer", "bi ", "business intelligence", "analytics",
        "statistician", "research scientist", "ai engineer", "nlp",
        "computer vision", "big data", "data architect",
    ]
    if any(kw in title_lower for kw in ds_keywords):
        return "data_science"
    
    # Web Dev keywords
    web_keywords = [
        "developer", "software engineer", "frontend", "backend",
        "full stack", "fullstack", "web", "devops", "sre",
        "react", "node", "python developer", "mobile",
        "android", "ios", "flutter", "application", "app dev",
        "microservices", "miniapps", "site reliability", "software",
        "programmer", "coding", "java developer", ".net",
    ]
    if any(kw in title_lower for kw in web_keywords):
        return "web_dev"
    
    # Cyber Security keywords
    sec_keywords = [
        "security", "cyber", "infosec", "soc", "penetration",
        "vulnerability", "ciso", "iam", "threat",
    ]
    if any(kw in title_lower for kw in sec_keywords):
        return "cyber_security"
    
    # Network & Systems keywords
    net_keywords = [
        "network", "infrastructure", "system admin", "sysadmin",
        "ict officer", "it officer", "information technology",
        "support", "help desk", "hardware", "telecom",
        "wireless", "cloud", "azure", "aws",
    ]
    if any(kw in title_lower for kw in net_keywords):
        return "network_systems"
    
    return "other"


def process_jobs(input_path: str, output_path: str) -> pd.DataFrame:
    """
    Process raw jobs data and save cleaned version.
    """
    print(f"Loading data from {input_path}...")
    df = pd.read_csv(input_path)
    
    print(f"Processing {len(df)} jobs...")
    
    # Extract company and job title from title column using "Hiring" pattern
    extracted = df["title"].apply(extract_company_from_title)
    df["company_clean"] = extracted.apply(lambda x: x[0])
    df["job_title_clean"] = extracted.apply(lambda x: x[1])
    
    # Normalize locations
    df["location_clean"] = df["location"].apply(normalize_location)
    
    # Classify domains (use cleaned job title for better accuracy)
    df["domain"] = df.apply(
        lambda row: classify_domain(
            row.get("job_title_clean", row.get("title", "")),
            row.get("career_track", "")
        ),
        axis=1
    )
    
    # Drop unnecessary columns
    columns_to_drop = ["salary_currency", "salary_text"]
    df = df.drop(columns=[c for c in columns_to_drop if c in df.columns], errors="ignore")
    
    # Fill salary NaN with 0
    for col in ["salary_min", "salary_max"]:
        if col in df.columns:
            df[col] = df[col].fillna(0).astype(int)
    
    # Reorder columns - put clean versions first
    priority_cols = [
        "id", "title", "job_title_clean", "company_clean", "location_clean", "domain",
        "experience_years_min", "experience_years_max", "education_level",
        "is_internship", "salary_min", "salary_max", "source", "url"
    ]
    other_cols = [c for c in df.columns if c not in priority_cols and c not in ["company", "location"]]
    final_cols = [c for c in priority_cols if c in df.columns] + other_cols
    df = df[final_cols]
    
    # Save cleaned data
    print(f"Saving cleaned data to {output_path}...")
    df.to_csv(output_path, index=False)
    
    # Print summary
    print("\n=== Data Cleaning Summary ===")
    print(f"Total jobs: {len(df)}")
    print(f"\nCompanies (top 15):")
    print(df["company_clean"].value_counts().head(15).to_string())
    print(f"\nUnknown companies: {(df['company_clean'] == 'Unknown').sum()}")
    print(f"\nLocations:")
    print(df["location_clean"].value_counts().to_string())
    print(f"\nDomains:")
    print(df["domain"].value_counts().to_string())
    
    return df


if __name__ == "__main__":
    # Run data processing
    base_path = Path(__file__).parent.parent / "data"
    input_path = base_path / "raw" / "jobs.csv"
    output_path = base_path / "processed" / "jobs_cleaned.csv"
    
    # Create output directory if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    process_jobs(str(input_path), str(output_path))
