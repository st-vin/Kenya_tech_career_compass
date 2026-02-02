# Kenya Tech Landscape Analysis 🇰🇪

A data-driven project to map the Kenyan technology job market, helping students and professionals navigate their careers with real-time insights.

## Overview

This project scrapes and analyzes job postings to provide clear, actionable insights into the skills, experience, and domains currently in demand in Kenya's tech ecosystem. 

**Primary Data Source:** `oyk.co.ke` (Online Jobs Kenya)
We focus exclusively on this source to ensure high-quality, relevant data for the local market.

## 🛠Dependencies & Installation

This project uses **[uv](https://github.com/astral-sh/uv)** for extremely fast dependency management.

### Prerequisites
- Python 3.8+
- `uv` (Universal Python Packaging)

### Setup Commands

1. **Clone the repository:**
   ```bash
   git clone https://github.com/st-vin/Kenya_tech_career_compass.git
   cd kenya-tech-landscape-v2
   ```

2. **Install dependencies with `uv`:**
   ```bash
   # Create a virtual environment and sync dependencies
   uv sync
   ```

   *Alternatively, if you are adding packages:*
   ```bash
   uv add streamlit pandas plotly beautifulsoup4 requests selenium webdriver-manager bs4 lxml
   ```

3. **Activate the environment:**
   *Windows:*
   ```pwsh
   .venv\Scripts\activate
   ```
   *Linux/Mac:*
   ```bash
   source .venv/bin/activate
   ```

## 🤖 Ethical Scraping & Compliance

We strictly adhere to `robots.txt` policies to ensure respectful usage of data sources. 

We adhere to the directives found in their `robots.txt`, including respecting the crawl delay.

## 🕷️ Running the Scraper

To fetch fresh job data from OYK, use the included `run_scraper.py` script.

### 1. Basic Usage (Scrape Internships)
By default, the scraper looks for the latest internships.
```bash
uv run python run_scraper.py --all
```

### 2. Advanced Usage
You can specify search queries, limits, and visibility.

**Search for specific jobs:**
```bash
uv run python run_scraper.py --mode search --query "software engineer"
```

**Run with browser visible (not headless):**
```bash
uv run python run_scraper.py --no-headless
```

**Limit the number of results:**
```bash
uv run python run_scraper.py --limit 50
```

## 🔄 Data Pipeline

To update the dashboard with fresh data, run the full pipeline:

### 1. Scrape Data
Fetch jobs from the web into the local database (`data/career_data.db`).
```bash
uv run python run_scraper.py --all
```

### 2. Export Data
Export the raw data from the database to CSV (`data/raw/jobs.csv`) for processing.
```bash
uv run python src/export_db.py
```

### 3. Clean Data
Standardize locations, company names, and tags (`data/processed/jobs_cleaned.csv`).
```bash
uv run python src/data_processor.py
```

### 4. Extract Skills
Analyze job descriptions to extract skills and generate summary stats (`data/processed/skills_v2.csv`).
```bash
uv run python src/skill_extractor.py
```

## 📊 Dashboard Walkthrough

The heart of this project is the interactive Dashboard. Here is how to use it:

### Launching the Dashboard

Run the following command from the project root:
```bash
streamlit run src/dashboard/app.py
```

### Dashboard Pages

1.  **What Should I Learn? (Skills Focus)**
    *   **Goal:** Discover the most valuable skills for your target role.
    *   **Features:**
        *   *Top Skills:* See ranked lists of "must-have" languages and frameworks.
        *   *Skill Pairs:* Find out "If I know Python, what should I learn next?" (e.g., Python + SQL).
        *   *Deep Dive:* Search for any specific skill to see its market demand.

2.  **Can I Get Hired? (Requirements Focus)**
    *   **Goal:** Assess your readiness for the market.
    *   **Features:**
        *   *Experience:* See the reality of "Entry Level" vs "Senior" roles.
        *   *Education:* Check if you *really* need a degree for Web Dev vs Data Science.
        *   *Accessibility:* Identify which domains are easiest to break into.

3.  **Where Should I Apply? (Market Focus)**
    *   **Goal:** Target the right companies and locations.
    *   **Features:**
        *   *Top Companies:* Identify who is hiring aggressively (e.g., Banks vs Startups).
        *   *Location:* Remote vs On-site trends.

## 💡 Why Use This Dashboard?

Whether you are a student, a career switcher, or a mentor, this tool answers the hard questions:

### 🎓 For Students & Bootcamp Grads
> *"I just finished a bootcamp in Python. Am I ready to apply?"*
*   **Answer:** Go to the **"Can I Get Hired?"** page. Look at the *Experience Distribution*. If 40% of Python jobs ask for 0-2 years experience, you have a green light! If it's mostly Senior roles, check the *Skill Pairs* to see what secondary skill (like Django or AWS) could bridge the gap.

### 🔄 For Career Switchers
> *"I want to get into Tech but I don't have a Computer Science Degree."*
*   **Answer:** Check the **"Education"** tab. You'll likely see that *Web Development* has a high percentage of "No Degree Specified" roles compared to *Data Science*. This supports pivoting into Web Dev first.

### 💼 For Job Seekers
> *"I'm sending out hundreds of applications and getting no response."*
*   **Answer:** Use **"Where Should I Apply?"** to find companies that are ACTUALLY hiring right now. Stop guessing and target the active recruiters.

---
*Empowering the Kenyan Tech Community with Data.* 🇰🇪
