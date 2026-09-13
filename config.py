"""
Configuration module for Play Store Review LLM Insights Miner.
Loads environment variables and sets project paths, defaults, and taxonomy.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"

# Ensure runtime directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# Load environment variables from .env if present
load_dotenv(BASE_DIR / ".env")

# App & Scraping Defaults
DEFAULT_APP_ID = "com.ubercab"  # Uber: Ride-hailing & Mobility
DEFAULT_REVIEW_COUNT = 300
DEFAULT_LANG = "en"
DEFAULT_COUNTRY = "us"

# LLM Defaults
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
DEFAULT_LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

# Data File Paths
RAW_REVIEWS_PATH = DATA_DIR / "raw_reviews.csv"
CLASSIFIED_REVIEWS_PATH = DATA_DIR / "classified_reviews.csv"
AGGREGATED_INSIGHTS_PATH = DATA_DIR / "aggregated_insights.csv"
VISUALIZATION_PATH = ASSETS_DIR / "complaint_clusters.png"

# Taxonomy Guidelines
FEATURE_AREAS = [
    "Billing & Payments",
    "Trip Experience & Drivers",
    "App Performance & Bugs",
    "Navigation & Geolocation",
    "Promotions & Dynamic Pricing",
    "Customer Support",
    "Account & Login",
    "General UI/UX"
]

SEVERITY_SCALE = {
    1: "Minor nuance or positive comment",
    2: "Mild inconvenience or UX friction",
    3: "Noticeable annoyance or repeated bug",
    4: "High disruption / ride failure / unexpected charge",
    5: "Critical failure / financial loss / account lockout / safety risk"
}
