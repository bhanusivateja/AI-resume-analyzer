"""
database.py - SQLite Storage for Local Analysis History
Safely logs analysis metadata, timestamps, and scores without storing raw PII or resume text.
"""

import sqlite3
import os
from contextlib import contextmanager
from datetime import datetime
from typing import List, Dict, Any, Optional, Generator
import pandas as pd


class DatabaseManager:
    """Manages SQLite database for local resume scan history."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, "data", "analysis_history.db")
        self.db_path = db_path
        self.init_db()

    @contextmanager
    def _get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager that guarantees the SQLite connection is closed."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def init_db(self) -> None:
        """Initialize SQLite table schema if not already present."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scan_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    candidate_name TEXT,
                    job_title TEXT,
                    overall_score REAL NOT NULL,
                    rating_label TEXT NOT NULL,
                    matched_count INTEGER DEFAULT 0,
                    missing_count INTEGER DEFAULT 0,
                    matched_preview TEXT,
                    missing_preview TEXT
                )
            """)
            conn.commit()

    def save_analysis(
        self,
        candidate_name: Optional[str],
        job_title: Optional[str],
        overall_score: float,
        rating_label: str,
        matched_skills: List[str],
        missing_skills: List[str]
    ) -> int:
        """Save a new scan entry to the database."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        name_clean = candidate_name.strip() if candidate_name else "Candidate"
        job_clean = job_title.strip() if job_title else "Software Engineer"
        matched_preview = ", ".join(matched_skills[:8])
        missing_preview = ", ".join(missing_skills[:8])

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO scan_history (
                    timestamp, candidate_name, job_title, overall_score,
                    rating_label, matched_count, missing_count,
                    matched_preview, missing_preview
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                now, name_clean, job_clean, float(overall_score),
                rating_label, len(matched_skills), len(missing_skills),
                matched_preview, missing_preview
            ))
            conn.commit()
            return cursor.lastrowid

    def get_all_analyses(self) -> List[Dict[str, Any]]:
        """Retrieve all previous scan entries ordered by most recent."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scan_history ORDER BY id DESC")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_history_df(self) -> pd.DataFrame:
        """Retrieve history as a pandas DataFrame."""
        records = self.get_all_analyses()
        if not records:
            return pd.DataFrame(columns=[
                "id", "timestamp", "candidate_name", "job_title",
                "overall_score", "rating_label", "matched_count", "missing_count"
            ])
        return pd.DataFrame(records)

    def delete_analysis(self, scan_id: int) -> bool:
        """Delete a single analysis entry by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM scan_history WHERE id = ?", (scan_id,))
            conn.commit()
            return cursor.rowcount > 0

    def clear_all(self) -> bool:
        """Clear the entire scan history table."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM scan_history")
            conn.commit()
            return True
