import pandas as pd
from pathlib import Path
from collections import Counter
from itertools import combinations

def load_data():
    base_path = Path("c:/Users/ADMIN/Documents/.Vin/kenya-tech-landscape-v2/data/processed")
    jobs = pd.read_csv(base_path / "jobs_cleaned.csv")
    skills = pd.read_csv(base_path / "skills_v2.csv")
    return jobs, skills

def debug_web_dev_pairs(jobs, skills):
    print("\n=== Debugging Web Dev Skill Pairs ===")
    
    # 1. Check Web Dev Jobs
    web_jobs = jobs[jobs["domain"] == "web_dev"]
    print(f"Total Web Dev Jobs: {len(web_jobs)}")
    
    if len(web_jobs) == 0:
        print("CRITICAL: No jobs found with domain='web_dev'")
        print("Available domains:", jobs["domain"].unique())
        return

    # 2. Check Skills for these jobs
    web_job_ids = web_jobs["id"].unique()
    web_skills = skills[skills["job_id"].isin(web_job_ids)]
    print(f"Total Skills for Web Dev jobs: {len(web_skills)}")
    
    # 3. Check Hard Skills
    hard_skills = web_skills[web_skills["category"] != "soft_skills"]
    print(f"Total Hard Skills for Web Dev jobs: {len(hard_skills)}")
    
    if len(hard_skills) == 0:
        print("CRITICAL: No hard skills found for Web Dev jobs")
        print("Sample categories found:", web_skills["category"].unique())
        return

    # 4. detailed check on pair generation
    job_skills_map = hard_skills.groupby("job_id")["skill_name"].apply(list)
    print(f"Jobs with at least one hard skill: {len(job_skills_map)}")
    
    pair_counts = Counter()
    pair_seen_count = 0
    for skills_list in job_skills_map:
        if len(skills_list) >= 2:
            pair_seen_count += 1
            for pair in combinations(set(skills_list), 2):
                pair_counts[tuple(sorted(pair))] += 1
                
    print(f"Jobs contributing to pairs (>=2 skills): {pair_seen_count}")
    print(f"Total unique pairs found: {len(pair_counts)}")
    print("Top 5 pairs found:", pair_counts.most_common(5))

def analyze_other_domain(jobs):
    print("\n=== Analyzing 'Other' Domain ===")
    other_jobs = jobs[jobs["domain"] == "other"]
    print(f"Total 'Other' jobs: {len(other_jobs)}")
    
    print("\nTop 30 Job Titles in 'Other':")
    print(other_jobs["job_title_clean"].value_counts().head(30).to_string())
    
    print("\nSample of raw titles for 'Other':")
    print(other_jobs["title"].head(20).to_string())

if __name__ == "__main__":
    jobs, skills = load_data()
    debug_web_dev_pairs(jobs, skills)
    analyze_other_domain(jobs)
