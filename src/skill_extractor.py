"""
Skill extractor using regex-based matching with comprehensive skill dictionaries.
Generates skills_v2.csv with fresh extraction.
"""
import pandas as pd
import re
from pathlib import Path
from typing import List, Dict, Set, Tuple
from collections import defaultdict

from skills_config import (
    DATA_SCIENCE_SKILLS,
    WEB_DEV_SKILLS,
    CYBER_SECURITY_SKILLS,
    SOFT_SKILLS,
    SKILL_VARIANTS,
    get_skill_lookup,
)

# Categories considered "hard skills"
HARD_SKILL_CATEGORIES = {
    # Data Science
    "languages", "ml_ai_frameworks", "data_processing", "visualization",
    "bi_tools", "big_data", "databases", "mlops",
    # Web Dev  
    "frontend_frameworks", "css_styling", "backend_frameworks",
    "devops_tools", "testing", "api_tools", "mobile",
    # Cyber Security
    "tools", "frameworks", "certifications",
}

# Categories that are NOT concepts/soft skills but are technical
TECHNICAL_CONCEPTS = {
    "concepts"  # Keep concepts but filter out non-technical ones
}


def build_skill_patterns() -> Dict[str, Tuple[re.Pattern, str, str]]:
    """
    Build compiled regex patterns for all skills.
    Returns dict: skill_name -> (pattern, domain, category)
    """
    patterns = {}
    
    def add_skills(skills_dict: dict, domain: str):
        for category, skill_list in skills_dict.items():
            for skill in skill_list:
                # Create word boundary pattern (case-insensitive)
                # Escape special regex chars
                escaped = re.escape(skill)
                # Handle skills with dots (e.g., "Node.js", "Vue.js")
                escaped = escaped.replace(r"\.js", r"\.?js")
                pattern = re.compile(rf"\b{escaped}\b", re.IGNORECASE)
                patterns[skill] = (pattern, domain, category)
    
    add_skills(DATA_SCIENCE_SKILLS, "data_science")
    add_skills(WEB_DEV_SKILLS, "web_dev")
    add_skills(CYBER_SECURITY_SKILLS, "cyber_security")
    
    # Add soft skills
    for skill in SOFT_SKILLS:
        escaped = re.escape(skill)
        pattern = re.compile(rf"\b{escaped}\b", re.IGNORECASE)
        patterns[skill] = (pattern, "general", "soft_skills")
    
    # Add variants (map to canonical form)
    for variant, canonical in SKILL_VARIANTS.items():
        if variant.lower() != canonical.lower():  # Skip if same
            escaped = re.escape(variant)
            pattern = re.compile(rf"\b{escaped}\b", re.IGNORECASE)
            # Find the original skill's domain/category
            if canonical in patterns:
                _, domain, category = patterns[canonical]
                patterns[f"__variant__{variant}"] = (pattern, domain, category, canonical)
    
    return patterns


def extract_skills_from_text(
    text: str,
    patterns: Dict[str, Tuple],
) -> List[Dict[str, str]]:
    """
    Extract skills from text using regex patterns.
    Returns list of dicts with skill_name, domain, category.
    """
    if pd.isna(text) or not text.strip():
        return []
    
    found_skills = {}  # Use dict to dedupe by canonical name
    
    for skill_key, pattern_info in patterns.items():
        if skill_key.startswith("__variant__"):
            pattern, domain, category, canonical = pattern_info
            if pattern.search(text):
                found_skills[canonical] = {
                    "skill_name": canonical,
                    "domain": domain,
                    "category": category,
                }
        else:
            pattern, domain, category = pattern_info
            if pattern.search(text):
                found_skills[skill_key] = {
                    "skill_name": skill_key,
                    "domain": domain,
                    "category": category,
                }
    
    return list(found_skills.values())


def extract_all_skills(
    jobs_df: pd.DataFrame,
    output_path: str,
) -> pd.DataFrame:
    """
    Extract skills from all job descriptions and save to CSV.
    """
    print("Building skill patterns...")
    patterns = build_skill_patterns()
    print(f"Total skill patterns: {len(patterns)}")
    
    all_skills = []
    skill_id = 1
    
    print(f"Extracting skills from {len(jobs_df)} jobs...")
    
    for idx, row in jobs_df.iterrows():
        job_id = row.get("id", idx + 1)
        description = row.get("description", "")
        title = row.get("title", "")
        
        # Combine title and description for matching
        full_text = f"{title} {description}"
        
        skills = extract_skills_from_text(full_text, patterns)
        
        for skill in skills:
            all_skills.append({
                "id": skill_id,
                "job_id": job_id,
                "skill_name": skill["skill_name"],
                "domain": skill["domain"],
                "category": skill["category"],
            })
            skill_id += 1
        
        if (idx + 1) % 50 == 0:
            print(f"  Processed {idx + 1}/{len(jobs_df)} jobs...")
    
    skills_df = pd.DataFrame(all_skills)
    
    # Save to CSV
    print(f"Saving {len(skills_df)} skill entries to {output_path}...")
    skills_df.to_csv(output_path, index=False)
    
    # Print summary
    print("\n=== Skill Extraction Summary ===")
    print(f"Total skill entries: {len(skills_df)}")
    print(f"Unique skills found: {skills_df['skill_name'].nunique()}")
    print(f"\nSkills per job (avg): {len(skills_df) / len(jobs_df):.1f}")
    
    print("\nTop 20 skills:")
    print(skills_df["skill_name"].value_counts().head(20).to_string())
    
    print("\nSkills by domain:")
    print(skills_df["domain"].value_counts().to_string())
    
    print("\nSkills by category:")
    print(skills_df["category"].value_counts().to_string())
    
    return skills_df


def generate_skills_summary(
    skills_df: pd.DataFrame,
    jobs_df: pd.DataFrame,
    output_path: str,
) -> pd.DataFrame:
    """
    Generate aggregated skills summary for dashboard.
    """
    print("Generating skills summary...")
    
    total_jobs = len(jobs_df)
    
    # Merge with jobs to get experience data
    jobs_subset = jobs_df[["id", "experience_years_min", "experience_years_max"]].copy()
    jobs_subset = jobs_subset.rename(columns={"id": "job_id"})
    
    merged = skills_df.merge(jobs_subset, on="job_id", how="left")
    
    # Aggregate by skill
    summary = merged.groupby(["skill_name", "domain", "category"]).agg(
        job_count=("job_id", "nunique"),
        avg_exp_min=("experience_years_min", "mean"),
        avg_exp_max=("experience_years_max", "mean"),
    ).reset_index()
    
    # Calculate percentage
    summary["pct_of_total"] = (summary["job_count"] / total_jobs * 100).round(1)
    
    # Round experience
    summary["avg_exp_min"] = summary["avg_exp_min"].round(1)
    summary["avg_exp_max"] = summary["avg_exp_max"].round(1)
    
    # Sort by job count
    summary = summary.sort_values("job_count", ascending=False)
    
    # Save
    print(f"Saving skills summary to {output_path}...")
    summary.to_csv(output_path, index=False)
    
    print(f"Summary contains {len(summary)} unique skills")
    
    return summary


def generate_cooccurrence(
    skills_df: pd.DataFrame, 
    output_path: str, 
    top_n: int = 30,
    hard_skills_only: bool = False,
    output_suffix: str = "",
):
    """
    Generate skill co-occurrence matrix for top skills.
    
    Args:
        skills_df: DataFrame with skill extractions
        output_path: Path to save results
        top_n: Number of top skills to include
        hard_skills_only: If True, exclude soft skills and only use technical skills
        output_suffix: Suffix to add to output filename
    """
    skill_type = "hard skills" if hard_skills_only else "all skills"
    print(f"Generating skill co-occurrence ({skill_type})...")
    
    # Filter to hard skills if requested
    if hard_skills_only:
        skills_filtered = skills_df[
            skills_df["category"].isin(HARD_SKILL_CATEGORIES) |
            (skills_df["category"] == "concepts")  # Include technical concepts
        ].copy()
        # Exclude certain generic concepts
        exclude_concepts = ["compliance", "audit", "agile", "scrum", "project management"]
        skills_filtered = skills_filtered[
            ~skills_filtered["skill_name"].str.lower().isin(exclude_concepts)
        ]
    else:
        skills_filtered = skills_df.copy()
    
    # Get top N skills
    top_skills = skills_filtered["skill_name"].value_counts().head(top_n).index.tolist()
    
    print(f"  Top {top_n} skills for co-occurrence:")
    for i, skill in enumerate(top_skills[:10], 1):
        count = skills_filtered[skills_filtered["skill_name"] == skill].shape[0]
        print(f"    {i}. {skill}: {count}")
    
    # Build job -> skills mapping
    job_skills = defaultdict(set)
    for _, row in skills_filtered.iterrows():
        if row["skill_name"] in top_skills:
            job_skills[row["job_id"]].add(row["skill_name"])
    
    # Count co-occurrences
    cooccurrence = defaultdict(int)
    skill_counts = defaultdict(int)
    
    for job_id, skills in job_skills.items():
        skills_list = list(skills)
        for skill in skills_list:
            skill_counts[skill] += 1
        for i, skill1 in enumerate(skills_list):
            for skill2 in skills_list[i+1:]:
                pair = tuple(sorted([skill1, skill2]))
                cooccurrence[pair] += 1
    
    # Convert to dataframe
    rows = []
    for (skill1, skill2), count in cooccurrence.items():
        # Calculate percentage based on the less common skill
        min_count = min(skill_counts[skill1], skill_counts[skill2])
        pct = (count / min_count * 100) if min_count > 0 else 0
        rows.append({
            "skill_1": skill1,
            "skill_2": skill2,
            "cooccurrence_count": count,
            "cooccurrence_pct": round(pct, 1),
        })
    
    df = pd.DataFrame(rows)
    df = df.sort_values("cooccurrence_count", ascending=False)
    
    # Modify output path if suffix provided
    if output_suffix:
        output_path = Path(output_path)
        output_path = output_path.parent / f"{output_path.stem}{output_suffix}{output_path.suffix}"
    
    print(f"Saving co-occurrence data to {output_path}...")
    df.to_csv(output_path, index=False)
    
    print(f"\nTop 10 skill pairs ({skill_type}):")
    print(df.head(10).to_string(index=False))
    
    return df


if __name__ == "__main__":
    # Run skill extraction
    base_path = Path(__file__).parent.parent / "data"
    
    # Load raw jobs (need description for extraction)
    jobs_path = base_path / "raw" / "jobs.csv"
    print(f"Loading jobs from {jobs_path}...")
    jobs_df = pd.read_csv(jobs_path)
    
    # Create output directory
    processed_path = base_path / "processed"
    processed_path.mkdir(parents=True, exist_ok=True)
    
    # Extract skills
    skills_v2_path = processed_path / "skills_v2.csv"
    skills_df = extract_all_skills(jobs_df, str(skills_v2_path))
    
    # Generate summary
    summary_path = processed_path / "skills_summary.csv"
    generate_skills_summary(skills_df, jobs_df, str(summary_path))
    
    # Generate co-occurrence - ALL skills
    cooccurrence_path = processed_path / "skill_cooccurrence.csv"
    generate_cooccurrence(skills_df, str(cooccurrence_path), hard_skills_only=False)
    
    # Generate co-occurrence - HARD SKILLS ONLY
    print("\n" + "="*50)
    generate_cooccurrence(
        skills_df, 
        str(cooccurrence_path), 
        hard_skills_only=True,
        output_suffix="_hard_skills"
    )
    
    print("\n✅ Skill extraction complete!")
