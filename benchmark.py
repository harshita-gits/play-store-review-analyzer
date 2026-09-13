"""
Multi-App Comparative Benchmarking Engine.
Compares user feedback and severity telemetry across two competing mobile applications.
Generates side-by-side comparative visualizations in assets/comparative_benchmark.png.
"""

import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from config import ASSETS_DIR
from scraper import fetch_reviews
from extractor import batch_process_reviews
from visualize import aggregate_complaints

BENCHMARK_CHART_PATH = ASSETS_DIR / "comparative_benchmark.png"


def run_benchmark(
    app_a: str = "com.ubercab",
    app_b: str = "com.dd.doordash",
    count: int = 150,
    output_chart=BENCHMARK_CHART_PATH
):
    """Run full comparative telemetry analysis between two mobile apps."""
    print(f"\n=======================================================")
    print(f" COMPARATIVE BENCHMARK: {app_a} vs. {app_b}")
    print(f"=======================================================\n")

    # 1. Fetch data
    print(f"[STEP 1/3] Scraping {count} reviews for App A: {app_a}...")
    df_a = fetch_reviews(app_id=app_a, count=count)
    df_a["app_name"] = app_a.split(".")[-1].capitalize()

    print(f"\n[STEP 1/3] Scraping {count} reviews for App B: {app_b}...")
    df_b = fetch_reviews(app_id=app_b, count=count)
    df_b["app_name"] = app_b.split(".")[-1].capitalize()

    # 2. Extract telemetry
    print(f"\n[STEP 2/3] Extracting structured telemetry for {app_a}...")
    classified_a = batch_process_reviews(df_a)

    print(f"\n[STEP 2/3] Extracting structured telemetry for {app_b}...")
    classified_b = batch_process_reviews(df_b)

    # 3. Combine and analyze
    combined = pd.concat([classified_a, classified_b], ignore_index=True)
    
    app_a_name = df_a["app_name"].iloc[0]
    app_b_name = df_b["app_name"].iloc[0]

    # Metrics Summary
    print("\n=======================================================")
    print(" EXECUTIVE BENCHMARK COMPARISON TABLE")
    print("=======================================================")
    summary = []
    for name, grp in combined.groupby("app_name"):
        tot = len(grp)
        neg = len(grp[grp["sentiment"] == "negative"])
        crit = len(grp[grp["severity"] >= 4])
        summary.append({
            "App": name,
            "Sample Size": tot,
            "Avg Star Rating": f"{grp['star_rating'].mean():.2f} / 5.0",
            "Negative Share": f"{(neg / tot) * 100:.1f}%",
            "Critical Severity (4-5)": f"{(crit / tot) * 100:.1f}%",
            "Avg Complaint Severity": f"{grp[grp['severity'] >= 2]['severity'].mean():.2f} / 5.0"
        })
    print(pd.DataFrame(summary).to_string(index=False))

    # 4. Render Visuals
    print(f"\n[STEP 3/3] Generating comparative visual dashboard...")
    sns.set_theme(style="whitegrid", font="sans-serif")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Panel 1: Star Rating Distribution
    sns.countplot(
        data=combined,
        x="star_rating",
        hue="app_name",
        palette=["#2563EB", "#F97316"],
        ax=ax1,
        edgecolor="#1E293B",
        linewidth=0.8
    )
    ax1.set_title("Customer Star Rating Distribution", fontsize=13, fontweight="bold", pad=12)
    ax1.set_xlabel("Star Rating (1 to 5 Stars)", fontsize=11, fontweight="bold")
    ax1.set_ylabel("Number of Reviews", fontsize=11, fontweight="bold")
    ax1.legend(title="Application")

    # Panel 2: Defect Share by Feature Area
    complaints = combined[combined["severity"] >= 2].copy()
    area_counts = (
        complaints.groupby(["feature_area", "app_name"], as_index=False)
        .size()
        .rename(columns={"size": "count"})
    )
    
    # Calculate percentage within each app
    totals = area_counts.groupby("app_name")["count"].transform("sum")
    area_counts["pct"] = (area_counts["count"] / totals) * 100

    sns.barplot(
        data=area_counts,
        y="feature_area",
        x="pct",
        hue="app_name",
        palette=["#2563EB", "#F97316"],
        ax=ax2,
        edgecolor="#1E293B",
        linewidth=0.8
    )
    ax2.set_title("Vulnerability Share by Feature Area (% of Complaints)", fontsize=13, fontweight="bold", pad=12)
    ax2.set_xlabel("% Share of App Complaints", fontsize=11, fontweight="bold")
    ax2.set_ylabel("")
    ax2.legend(title="Application")

    plt.suptitle(f"Competitive Telemetry Benchmark: {app_a_name} vs. {app_b_name}", fontsize=15, fontweight="heavy", y=1.02)
    plt.tight_layout()

    plt.savefig(output_chart, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[SAVED] Comparative benchmark chart rendered to: {output_chart}\n")


def main():
    parser = argparse.ArgumentParser(description="Benchmark two Google Play Store apps using LLM review telemetry.")
    parser.add_argument("--app-a", type=str, default="com.ubercab", help="Primary App package ID (e.g. com.ubercab)")
    parser.add_argument("--app-b", type=str, default="com.dd.doordash", help="Competitor App package ID (e.g. com.dd.doordash)")
    parser.add_argument("--count", type=int, default=100, help="Number of reviews to scrape per app")
    args = parser.parse_args()

    run_benchmark(app_a=args.app_a, app_b=args.app_b, count=args.count)


if __name__ == "__main__":
    main()
