"""
Export data from SQLite database to CSV for processing.
"""
import pandas as pd
import sqlite3
import sys
from pathlib import Path

# Add parent directory to path to enable imports
PACKAGE_DIR = Path(__file__).parent.parent
if str(PACKAGE_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGE_DIR))

from database import get_db, DB_PATH

def export_jobs_to_csv(output_path: str):
    """Export all jobs from database to CSV."""
    print(f"Connecting to database at {DB_PATH}...")
    
    # Use pandas to read sql
    conn = sqlite3.connect(DB_PATH)
    
    try:
        print("Reading jobs table...")
        df = pd.read_sql_query("SELECT * FROM jobs", conn)
        
        print(f"Found {len(df)} jobs.")
        
        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        print(f"Saving to {output_path}...")
        df.to_csv(output_path, index=False)
        print("✅ Export complete.")
        
    except Exception as e:
        print(f"❌ Error exporting data: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    base_path = Path(__file__).parent.parent / "data"
    output_path = base_path / "raw" / "jobs.csv"
    
    export_jobs_to_csv(str(output_path))
