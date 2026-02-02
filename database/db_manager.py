
import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "data" / "career_data.db"

class DBManager:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_db()
        
    def _get_conn(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        return sqlite3.connect(str(self.db_path))
        
    def _init_db(self):
        conn = self._get_conn()
        cur = conn.cursor()
        
        # Jobs Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                company TEXT,
                location TEXT,
                description TEXT,
                url TEXT UNIQUE,
                source TEXT,
                date_posted TIMESTAMP,
                date_scraped TIMESTAMP,
                salary_min REAL,
                salary_max REAL,
                salary_currency TEXT,
                experience_years_min INTEGER,
                career_track TEXT,
                is_internship BOOLEAN
            )
        """)
        
        # Skills Table (Linked to Jobs)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS job_skills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER,
                skill_name TEXT,
                skill_category TEXT,
                FOREIGN KEY(job_id) REFERENCES jobs(id)
            )
        """)
        
        # Scrape Log Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS scrape_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,
                query TEXT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                jobs_found INTEGER,
                jobs_saved INTEGER,
                errors INTEGER,
                status TEXT,
                error_message TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        
    def add_job(self, job_data: Dict[str, Any], skills: List[Dict] = None, requirements=None) -> Optional[int]:
        conn = self._get_conn()
        cur = conn.cursor()
        
        try:
            # Check if exists by URL
            cur.execute("SELECT id FROM jobs WHERE url = ?", (job_data.get('url'),))
            if cur.fetchone():
                return None
                
            cur.execute("""
                INSERT INTO jobs (
                    title, company, location, description, url, source, 
                    date_posted, date_scraped, salary_min, salary_max, salary_currency,
                    experience_years_min, career_track, is_internship
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job_data.get('title'), job_data.get('company'), job_data.get('location'), 
                job_data.get('description'), job_data.get('url'), job_data.get('source'),
                job_data.get('date_posted'), datetime.utcnow(), job_data.get('salary_min'),
                job_data.get('salary_max'), job_data.get('salary_currency'),
                job_data.get('experience_years_min'), job_data.get('career_track'),
                job_data.get('is_internship')
            ))
            
            job_id = cur.lastrowid
            
            if skills:
                for skill in skills:
                    cur.execute("""
                        INSERT INTO job_skills (job_id, skill_name, skill_category)
                        VALUES (?, ?, ?)
                    """, (job_id, skill.get('skill_name'), skill.get('skill_category')))
            
            conn.commit()
            return job_id
            
        except Exception as e:
            logger.error(f"DB Error: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    def get_job_by_url(self, url: str):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM jobs WHERE url = ?", (url,))
        res = cur.fetchone()
        conn.close()
        return res
        
    def start_scrape_log(self, source: str, query: str) -> int:
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO scrape_logs (source, query, start_time, status)
            VALUES (?, ?, ?, 'running')
        """, (source, query, datetime.utcnow()))
        log_id = cur.lastrowid
        conn.commit()
        conn.close()
        return log_id
        
    def update_scrape_log(self, log_id: int, **kwargs):
        conn = self._get_conn()
        cur = conn.cursor()
        
        fields = []
        values = []
        for k, v in kwargs.items():
            fields.append(f"{k} = ?")
            values.append(v)
            
        values.append(datetime.utcnow()) # End time
        values.append(log_id)
        
        cur.execute(f"""
            UPDATE scrape_logs 
            SET {', '.join(fields)}, end_time = ?
            WHERE id = ?
        """, tuple(values))
        conn.commit()
        conn.close()

    def get_scrape_stats(self) -> Dict[str, Any]:
        """Get statistics about scraped data."""
        conn = self._get_conn()
        cur = conn.cursor()
        
        stats = {
            "total_jobs": 0,
            "with_salary": 0,
            "internships": 0,
            "by_source": {},
            "by_track": {}
        }
        
        try:
            # Total jobs
            cur.execute("SELECT COUNT(*) FROM jobs")
            stats["total_jobs"] = cur.fetchone()[0]
            
            # With salary
            cur.execute("SELECT COUNT(*) FROM jobs WHERE salary_min IS NOT NULL OR salary_max IS NOT NULL")
            stats["with_salary"] = cur.fetchone()[0]
            
            # Internships
            cur.execute("SELECT COUNT(*) FROM jobs WHERE is_internship = 1")
            stats["internships"] = cur.fetchone()[0]
            
            # By Source
            cur.execute("SELECT source, COUNT(*) FROM jobs GROUP BY source")
            for row in cur.fetchall():
                stats["by_source"][row[0]] = row[1]
                
            # By Track
            cur.execute("SELECT career_track, COUNT(*) FROM jobs GROUP BY career_track")
            for row in cur.fetchall():
                stats["by_track"][row[0]] = row[1]
                
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
        finally:
            conn.close()
            
        return stats

# Stubs for type hinting in other files
class Job: pass
class Skill: pass

def get_db():
    return DBManager()
