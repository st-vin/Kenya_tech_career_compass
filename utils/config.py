
# Configuration for Scraper

SCRAPE_CONFIG = {
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "delay_min": 2,
    "delay_max": 5,
    "timeout": 15
}

# Define skills directly here to avoid import issues for now, or copy structure from src/skills_config.py
# Using a simplified version for restoration.

HARD_SKILLS = {
    "languages": [
        "Python", "R", "SQL", "Julia", "Scala", "Java", "JavaScript", "TypeScript", 
        "C++", "C#", "Go", "Rust", "PHP", "Ruby", "Swift", "Kotlin"
    ],
    "frameworks": [
        "React", "Angular", "Vue.js", "Django", "Flask", "Spring Boot", "Laravel", 
        "TensorFlow", "PyTorch", "scikit-learn", "Pandas", "NumPy", "Spark"
    ],
    "cloud_devops": [
        "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Jenkins", "Git", "CI/CD",
        "Terraform", "Ansible"
    ],
    "databases": [
        "PostgreSQL", "MySQL", "MongoDB", "Redis", "Oracle", "SQL Server", "DynamoDB"
    ]
}

SOFT_SKILLS = [
    "communication", "teamwork", "leadership", "problem solving",
    "critical thinking", "adaptability", "collaboration",
    "time management", "attention to detail", "presentation"
]

CAREER_TRACKS = {
    "data_science": ["data scientist", "data analyst", "machine learning", "ai engineer"],
    "web_dev": ["frontend", "backend", "full stack", "web developer", "software engineer"],
    "cyber_security": ["cyber security", "security engineer", "penetration tester", "infosec"],
    "network_systems": ["network engineer", "systems administrator", "devops engineer"]
}
