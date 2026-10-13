"""
skill_extractor.py - Robust, Multi-Category Skill Extraction with Alias Mapping
Handles special symbols (C++, C#, .NET), canonical normalization, and categorization.
"""

import json
import os
import re
from typing import Dict, List, Set, Any, Optional, Tuple


class SkillExtractor:
    """Extracts, normalizes, and categorizes skills from text."""

    # Pre-defined aliases mapping informal/shorthand terms to canonical names
    ALIASES = {
        "react.js": "React",
        "reactjs": "React",
        "nextjs": "Next.js",
        "next.js": "Next.js",
        "vuejs": "Vue.js",
        "vue": "Vue.js",
        "node": "Node.js",
        "nodejs": "Node.js",
        "expressjs": "Express.js",
        "express": "Express.js",
        "golang": "Go",
        "k8s": "Kubernetes",
        "amazon web services": "AWS",
        "google cloud platform": "GCP",
        "google cloud": "GCP",
        "microsoft azure": "Azure",
        "sklearn": "Scikit-learn",
        "postgres": "PostgreSQL",
        "postgre": "PostgreSQL",
        "mongo": "MongoDB",
        "restful api": "REST API",
        "restful apis": "REST API",
        "rest apis": "REST API",
        "rest api": "REST API",
        "generative ai": "Generative AI",
        "genai": "Generative AI",
        "llms": "LLM",
        "llm": "LLM",
        "large language models": "LLM",
        "deep learning": "Deep Learning",
        "machine learning": "Machine Learning",
        "artificial intelligence": "Artificial Intelligence",
        "nlp": "Natural Language Processing",
        "natural language processing": "Natural Language Processing",
        "computer vision": "Computer Vision",
        "cv": "Computer Vision",
        "ci/cd": "CI/CD",
        "cicd": "CI/CD",
        "continuous integration": "CI/CD",
        "oop": "Object-Oriented Programming",
        "object-oriented programming": "Object-Oriented Programming",
        "tdd": "Test-Driven Development",
        "test-driven development": "Test-Driven Development"
    }

    def __init__(self, skills_data_path: Optional[str] = None):
        """Initialize extractor with path to skills json or default."""
        if skills_data_path is None:
            # Look in data/skills.json relative to this file's root
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            skills_data_path = os.path.join(base_dir, "data", "skills.json")

        self.skills_data_path = skills_data_path
        self.categories: Dict[str, List[str]] = {}
        self.all_skills: Set[str] = set()
        self.skill_to_category: Dict[str, str] = {}
        self._load_skills()

    def _load_skills(self) -> None:
        """Load skills from JSON file and populate mappings."""
        if os.path.exists(self.skills_data_path):
            try:
                with open(self.skills_data_path, "r", encoding="utf-8") as f:
                    self.categories = json.load(f)
            except Exception:
                self.categories = self._fallback_skills()
        else:
            self.categories = self._fallback_skills()

        # Build skill lookups
        for category, skill_list in self.categories.items():
            for skill in skill_list:
                canonical = self.ALIASES.get(skill.lower(), skill)
                self.all_skills.add(canonical)
                self.skill_to_category[canonical.lower()] = category

    def _fallback_skills(self) -> Dict[str, List[str]]:
        """Fallback skill taxonomy if JSON file is missing."""
        return {
            "Programming Languages": ["Python", "Java", "C++", "C#", "JavaScript", "TypeScript", "SQL", "Go", "Rust"],
            "Web & Frameworks": ["React", "Node.js", "Django", "FastAPI", "Flask", "Express.js", "HTML", "CSS"],
            "AI & Machine Learning": ["Machine Learning", "Deep Learning", "PyTorch", "TensorFlow", "Scikit-learn", "Pandas", "NumPy", "NLP"],
            "Cloud & DevOps": ["AWS", "Azure", "Docker", "Kubernetes", "CI/CD", "Git", "Linux"],
            "Databases & Data Engineering": ["PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite"],
            "Tools & Developer Practices": ["Git", "GitHub", "Jira", "Postman", "Agile", "Unit Testing"],
            "Soft Skills & Core Competencies": ["Problem Solving", "Effective Communication", "Team Collaboration", "Leadership"]
        }

    def _build_regex(self, term: str) -> re.Pattern:
        """
        Build a robust regex for a skill term handling punctuation and boundaries.
        Special care for C++, C#, .NET, Node.js, CI/CD.
        """
        escaped = re.escape(term)
        # If term ends with + or #, normal \b won't match after it
        if term.endswith("+") or term.endswith("#"):
            pattern = rf"(?:^|[\s,;/()\[\]]){escaped}(?:$|[\s,;/()\[\]])"
        elif term.startswith("."):
            pattern = rf"(?:^|[\s,;/()\[\]]){escaped}\b"
        else:
            pattern = rf"\b{escaped}\b"

        return re.compile(pattern, re.IGNORECASE)

    def extract_skills_from_text(self, text: str) -> Dict[str, Any]:
        """
        Extract skills from text, normalize them to canonical names,
        categorize them, and calculate frequencies.
        """
        if not text:
            return {
                "skills": [],
                "categorized": {},
                "count": 0,
                "frequencies": {}
            }

        extracted_set: Set[str] = set()
        frequencies: Dict[str, int] = {}

        # 1. Check all canonical skills and aliases in taxonomy
        search_terms = {}
        for category, skill_list in self.categories.items():
            for skill in skill_list:
                canonical = self.ALIASES.get(skill.lower(), skill)
                search_terms[skill] = canonical

        # Add explicit aliases
        for alias, canonical in self.ALIASES.items():
            search_terms[alias] = canonical

        for term, canonical in search_terms.items():
            pattern = self._build_regex(term)
            matches = pattern.findall(text)
            if matches:
                count = len(matches)
                extracted_set.add(canonical)
                frequencies[canonical] = frequencies.get(canonical, 0) + count

        # Organize by category
        categorized: Dict[str, List[str]] = {cat: [] for cat in self.categories.keys()}
        categorized["Other / Custom"] = []

        for skill in sorted(extracted_set, key=lambda s: s.lower()):
            cat = self.skill_to_category.get(skill.lower(), "Other / Custom")
            if cat not in categorized:
                categorized[cat] = []
            categorized[cat].append(skill)

        # Filter empty categories
        categorized = {k: v for k, v in categorized.items() if len(v) > 0}

        return {
            "skills": sorted(list(extracted_set)),
            "categorized": categorized,
            "count": len(extracted_set),
            "frequencies": frequencies
        }

    def add_custom_skill(self, skill_name: str, category: str = "Other / Custom") -> None:
        """Add a custom user-defined skill to runtime extractor."""
        clean_name = skill_name.strip()
        if not clean_name:
            return

        canonical = self.ALIASES.get(clean_name.lower(), clean_name)
        self.all_skills.add(canonical)
        self.skill_to_category[canonical.lower()] = category
        if category not in self.categories:
            self.categories[category] = []
        if canonical not in self.categories[category]:
            self.categories[category].append(canonical)
