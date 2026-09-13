"""
Play Store Review Scraper.
Uses 'google-play-scraper' to fetch recent public reviews for any Google Play Store application.
"""

import argparse
import sys
from typing import List, Dict, Any
import pandas as pd
from google_play_scraper import reviews, Sort

from config import DEFAULT_APP_ID, DEFAULT_REVIEW_COUNT, DEFAULT_LANG, DEFAULT_COUNTRY, RAW_REVIEWS_PATH


def fetch_reviews(
    app_id: str = DEFAULT_APP_ID,
    count: int = DEFAULT_REVIEW_COUNT,
    lang: str = DEFAULT_LANG,
    country: str = DEFAULT_COUNTRY,
    sort: Sort = Sort.NEWEST
) -> pd.DataFrame:
    """
    Fetch public reviews for a specified Android app package ID.
    
    Args:
        app_id: The Play Store package identifier (e.g. 'com.ubercab')
        count: Desired number of reviews (e.g. 200 to 500)
        lang: Review language code
        country: Two-letter country code
        sort: Sort.NEWEST or Sort.MOST_RELEVANT
        
    Returns:
        pd.DataFrame containing cleaned review records
    """
    print(f"[INFO] Scraping {count} reviews for app '{app_id}' (lang={lang}, country={country})...")
    
    try:
        results, continuation_token = reviews(
            app_id,
            lang=lang,
            country=country,
            sort=sort,
            count=count
        )
    except Exception as e:
        print(f"[ERROR] Failed to fetch reviews for {app_id}: {e}", file=sys.stderr)
        raise

    if not results:
        print(f"[WARNING] No reviews returned for app '{app_id}'.")
        return pd.DataFrame()

    print(f"[SUCCESS] Scraped {len(results)} raw reviews successfully.")
    
    # Extract relevant fields
    records: List[Dict[str, Any]] = []
    for r in results:
        text = (r.get("content") or "").strip()
        if not text:
            continue
            
        records.append({
            "review_id": r.get("reviewId"),
            "user_name": r.get("userName"),
            "content": text,
            "star_rating": r.get("score"),
            "thumbs_up": r.get("thumbsUpCount", 0),
            "review_date": str(r.get("at")),
            "app_version": r.get("reviewCreatedVersion") or "Unknown"
        })
        
    df = pd.DataFrame(records)
    print(f"[INFO] Cleaned dataset contains {len(df)} non-empty reviews.")
    return df


def save_reviews(df: pd.DataFrame, output_path=RAW_REVIEWS_PATH) -> None:
    """Save scraped reviews dataframe to CSV."""
    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"[SAVED] Raw reviews written to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Scrape Google Play Store reviews for LLM analysis.")
    parser.add_argument("--app-id", type=str, default=DEFAULT_APP_ID, help="Google Play Store package name")
    parser.add_argument("--count", type=int, default=DEFAULT_REVIEW_COUNT, help="Number of reviews to fetch (200-500)")
    parser.add_argument("--output", type=str, default=str(RAW_REVIEWS_PATH), help="Destination CSV file path")
    args = parser.parse_args()

    df = fetch_reviews(app_id=args.app_id, count=args.count)
    if not df.empty:
        save_reviews(df, args.output)


if __name__ == "__main__":
    main()
