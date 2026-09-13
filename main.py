"""
Main CLI Orchestrator for LLM Review-Insights Miner.
Executes the end-to-end pipeline:
1. Scrape Play Store Reviews
2. Batch Process & Classify using LLM Structured Prompting
3. Aggregate Pain Points & Compute Severity-Weighted Impact
4. Generate Executive Visualizations & Product Recommendations
"""

import argparse
import sys
from pathlib import Path
import pandas as pd

from config import (
    DEFAULT_APP_ID,
    DEFAULT_REVIEW_COUNT,
    RAW_REVIEWS_PATH,
    CLASSIFIED_REVIEWS_PATH,
    AGGREGATED_INSIGHTS_PATH,
    VISUALIZATION_PATH
)
from scraper import fetch_reviews, save_reviews
from extractor import batch_process_reviews
from visualize import run_analysis


def main():
    parser = argparse.ArgumentParser(
        description="LLM Review-Insights Miner: Mine Play Store reviews to cluster complaints and surface actionable product insights."
    )
    parser.add_argument("--app-id", type=str, default=DEFAULT_APP_ID, help="Google Play Store package name (default: com.ubercab)")
    parser.add_argument("--count", type=int, default=DEFAULT_REVIEW_COUNT, help="Number of reviews to scrape (default: 300)")
    parser.add_argument("--skip-scrape", action="store_true", help="Skip live scraping and reuse existing raw_reviews.csv")
    parser.add_argument("--skip-extract", action="store_true", help="Skip LLM extraction and reuse existing classified_reviews.csv")
    parser.add_argument("--limit", type=int, default=None, help="Optional limit on reviews to classify (for testing)")
    args = parser.parse_args()

    print("==================================================================")
    print("           LLM REVIEW-INSIGHTS MINER: PIPELINE RUNNER             ")
    print("==================================================================")

    # -------------------------------------------------------------------------
    # Step 1: Data Acquisition (Scraper)
    # -------------------------------------------------------------------------
    if not args.skip_scrape:
        print(f"\n[STEP 1/4] Scraping recent public reviews for '{args.app_id}'...")
        raw_df = fetch_reviews(app_id=args.app_id, count=args.count)
        if raw_df.empty:
            print("[ERROR] No reviews obtained. Aborting pipeline.", file=sys.stderr)
            sys.exit(1)
        save_reviews(raw_df, RAW_REVIEWS_PATH)
    else:
        print(f"\n[STEP 1/4] Skipping scrape. Loading existing raw reviews from: {RAW_REVIEWS_PATH}")
        if not RAW_REVIEWS_PATH.exists():
            print(f"[ERROR] {RAW_REVIEWS_PATH} not found! Remove --skip-scrape.", file=sys.stderr)
            sys.exit(1)
        raw_df = pd.read_csv(RAW_REVIEWS_PATH)

    print(f"[STATUS] Raw dataset loaded: {len(raw_df)} reviews.")

    # -------------------------------------------------------------------------
    # Step 2: LLM Structured Extraction
    # -------------------------------------------------------------------------
    if not args.skip_extract:
        print(f"\n[STEP 2/4] Classifying reviews into structured themes and severity...")
        classified_df = batch_process_reviews(raw_df, sample_limit=args.limit)
        classified_df.to_csv(CLASSIFIED_REVIEWS_PATH, index=False)
        print(f"[SAVED] Classified dataset saved to: {CLASSIFIED_REVIEWS_PATH}")
    else:
        print(f"\n[STEP 2/4] Skipping extraction. Loading existing classifications from: {CLASSIFIED_REVIEWS_PATH}")
        if not CLASSIFIED_REVIEWS_PATH.exists():
            print(f"[ERROR] {CLASSIFIED_REVIEWS_PATH} not found! Remove --skip-extract.", file=sys.stderr)
            sys.exit(1)

    # -------------------------------------------------------------------------
    # Step 3 & 4: Aggregation & Visualization
    # -------------------------------------------------------------------------
    print(f"\n[STEP 3/4 & 4/4] Aggregating insights and rendering publication dashboard...")
    run_analysis(
        classified_csv=CLASSIFIED_REVIEWS_PATH,
        insights_csv=AGGREGATED_INSIGHTS_PATH,
        chart_png=VISUALIZATION_PATH
    )

    print("\n==================================================================")
    print("                     PIPELINE COMPLETE!                           ")
    print("==================================================================")
    print(f"1. Raw Dataset:         {RAW_REVIEWS_PATH}")
    print(f"2. Classified Dataset:  {CLASSIFIED_REVIEWS_PATH}")
    print(f"3. Aggregated Metrics:  {AGGREGATED_INSIGHTS_PATH}")
    print(f"4. Dashboard Chart:     {VISUALIZATION_PATH}")
    print("==================================================================\n")


if __name__ == "__main__":
    main()
