"""
Aggregation and Visualization Module for LLM Review Insights.
Calculates frequency, average severity, and severity-weighted impact scores,
and generates presentation-ready figures using matplotlib and seaborn.
"""

import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from config import (
    CLASSIFIED_REVIEWS_PATH,
    AGGREGATED_INSIGHTS_PATH,
    VISUALIZATION_PATH
)


def aggregate_complaints(df: pd.DataFrame) -> pd.DataFrame:
    """
    Group reviews by theme, computing frequency, average severity,
    and a severity-weighted impact score (frequency * avg_severity).
    """
    # Focus analysis on complaints (negative or severity >= 2)
    complaints = df[df["severity"] >= 2].copy()
    if complaints.empty:
        complaints = df.copy()

    total_complaints = len(complaints)

    summary = (
        complaints.groupby("theme", as_index=False)
        .agg(
            feature_area=("feature_area", lambda x: x.mode()[0] if not x.empty else "General UI/UX"),
            frequency=("review_id", "count"),
            avg_severity=("severity", "mean"),
            min_stars=("star_rating", "min"),
            avg_stars=("star_rating", "mean")
        )
    )

    # Calculate severity-weighted impact score
    summary["impact_score"] = summary["frequency"] * summary["avg_severity"]
    summary["complaint_share_pct"] = (summary["frequency"] / total_complaints) * 100

    # Sort descending by impact score
    summary = summary.sort_values(by=["impact_score", "frequency"], ascending=False).reset_index(drop=True)
    return summary


def plot_complaint_clusters(summary_df: pd.DataFrame, output_path=VISUALIZATION_PATH) -> Path:
    """
    Generate a high-resolution, publication-grade visualization showing:
    1. Top Complaint Themes by Frequency & Severity (Key Case Study Visual)
    2. Severity-Weighted Impact by Feature Area
    """
    # Exclude or keep top specific themes
    top_themes = summary_df.head(9).copy()
    top_themes = top_themes.sort_values(by="impact_score", ascending=True)  # for horizontal bar chart

    # Set modern plotting theme
    sns.set_theme(style="whitegrid", font="sans-serif")
    plt.rcParams["font.family"] = "sans-serif"

    fig, (ax1, ax2) = plt.subplots(
        nrows=1,
        ncols=2,
        figsize=(17, 7.5),
        gridspec_kw={"width_ratios": [1.45, 1.0]}
    )

    # --- Panel 1: Key Visual - Top Complaint Themes (Frequency & Avg Severity) ---
    norm = plt.Normalize(vmin=2.5, vmax=5.0)
    cmap = plt.cm.plasma

    y_pos = range(len(top_themes))
    bars = ax1.barh(
        y_pos,
        top_themes["frequency"],
        color=cmap(norm(top_themes["avg_severity"])),
        edgecolor="#1E293B",
        linewidth=0.8,
        height=0.58
    )

    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(top_themes["theme"], fontsize=10.5, fontweight="500")

    # Annotate bars with frequency and average severity badge
    max_freq = top_themes["frequency"].max()
    for bar, (_, row) in zip(bars, top_themes.iterrows()):
        w = bar.get_width()
        sev = row["avg_severity"]
        ax1.text(
            w + (max_freq * 0.02),
            bar.get_y() + bar.get_height() / 2,
            f"{int(w)} reviews  |  Severity: {sev:.1f}/5.0",
            va="center",
            ha="left",
            fontsize=9.5,
            fontweight="bold",
            color="#0F172A"
        )

    ax1.set_title("Top User Complaint Themes (Frequency vs. Severity)", fontsize=13, fontweight="bold", pad=14)
    ax1.set_xlabel("Review Frequency (Count)", fontsize=11, fontweight="bold", labelpad=8)
    ax1.set_ylabel("Identified Complaint Theme", fontsize=11, fontweight="bold", labelpad=8)
    ax1.set_xlim(0, max_freq * 1.45)
    ax1.grid(axis="x", linestyle="--", alpha=0.5)

    # Colorbar for Severity
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax1, orientation="horizontal", pad=0.15, shrink=0.75)
    cbar.set_label("Average Severity Rating (1.0: Cosmetic  ->  5.0: Critical Loss/Safety)", fontsize=9.5, labelpad=5)

    # --- Panel 2: Impact by Product Feature Area ---
    area_agg = (
        summary_df.groupby("feature_area", as_index=False)
        .agg(total_volume=("frequency", "sum"), area_impact=("impact_score", "sum"))
        .sort_values(by="area_impact", ascending=False)
    )

    palette = sns.color_palette("mako", n_colors=len(area_agg))
    sns.barplot(
        data=area_agg,
        x="area_impact",
        y="feature_area",
        hue="feature_area",
        legend=False,
        ax=ax2,
        palette=palette,
        edgecolor="#1E293B",
        linewidth=0.8
    )

    max_impact = area_agg["area_impact"].max()
    for i, row in area_agg.reset_index(drop=True).iterrows():
        ax2.text(
            row["area_impact"] + (max_impact * 0.02),
            i,
            f"Impact: {row['area_impact']:.0f} ({int(row['total_volume'])} reviews)",
            va="center",
            fontsize=9.5,
            fontweight="semibold",
            color="#0F172A"
        )

    ax2.set_title("Severity-Weighted Impact by Product Feature Area", fontsize=13, fontweight="bold", pad=14)
    ax2.set_xlabel("Impact Score (Volume × Avg Severity)", fontsize=11, fontweight="bold", labelpad=8)
    ax2.set_ylabel("", fontsize=11)
    ax2.set_xlim(0, max_impact * 1.40)
    ax2.grid(axis="x", linestyle="--", alpha=0.5)

    plt.suptitle("LLM Review-Insights Miner: Executive Problem Prioritization Matrix", fontsize=15, fontweight="heavy", y=1.01)
    plt.tight_layout()

    # Save visualization
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[SAVED] Publication chart rendered to: {output_path}")
    return Path(output_path)


def generate_insights_report(summary_df: pd.DataFrame) -> None:
    """Print top pain point summary directly to console."""
    print("\n=======================================================")
    print(" EXECUTIVE PRODUCT INSIGHTS & COMPLAINT CLUSTERS")
    print("=======================================================")
    for i, row in summary_df.head(5).iterrows():
        print(f"#{i+1}: {row['theme']} [{row['feature_area']}]")
        print(f"    - Frequency: {int(row['frequency'])} reviews ({row['complaint_share_pct']:.1f}% of total complaints)")
        print(f"    - Avg Severity: {row['avg_severity']:.2f} / 5.0")
        print(f"    - Severity-Weighted Impact Score: {row['impact_score']:.1f}\n")


def run_analysis(
    classified_csv=CLASSIFIED_REVIEWS_PATH,
    insights_csv=AGGREGATED_INSIGHTS_PATH,
    chart_png=VISUALIZATION_PATH
):
    """Run full aggregation and visualization pipeline."""
    if not Path(classified_csv).exists():
        print(f"[ERROR] Classified reviews file not found at: {classified_csv}", file=sys.stderr)
        return

    df = pd.read_csv(classified_csv)
    summary = aggregate_complaints(df)
    summary.to_csv(insights_csv, index=False)
    print(f"[SAVED] Aggregated metrics written to: {insights_csv}")

    generate_insights_report(summary)
    plot_complaint_clusters(summary, chart_png)


if __name__ == "__main__":
    run_analysis()
