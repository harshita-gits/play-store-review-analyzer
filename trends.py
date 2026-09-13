"""
Release Regression and Version Telemetry Analyzer.
Tracks customer sentiment, defect share, and severity shifts across app release versions
to isolate newly introduced regressions and track quality recovery.
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from config import CLASSIFIED_REVIEWS_PATH, ASSETS_DIR

TRENDS_CHART_PATH = ASSETS_DIR / "version_trends.png"


def analyze_version_regressions(
    csv_path=CLASSIFIED_REVIEWS_PATH,
    output_chart=TRENDS_CHART_PATH
):
    """Analyze defect trends across mobile application releases."""
    if not Path(csv_path).exists():
        print(f"[ERROR] {csv_path} not found.")
        return

    df = pd.read_csv(csv_path)

    # Filter for top versions with significant sample size (>= 10 reviews)
    version_counts = df["app_version"].value_counts()
    valid_versions = version_counts[version_counts >= 10].index.tolist()
    
    # Exclude 'Unknown' if we have enough versioned data
    valid_versions = [v for v in valid_versions if v != "Unknown"]

    if len(valid_versions) < 2:
        print("[INFO] Less than 2 distinct version tags found; analyzing all non-empty versions.")
        valid_versions = version_counts.head(3).index.tolist()

    sub_df = df[df["app_version"].isin(valid_versions)].copy()

    print(f"\n=======================================================")
    print(f" RELEASE REGRESSION ANALYSIS ({', '.join(valid_versions)})")
    print(f"=======================================================\n")

    summary = []
    for ver, grp in sub_df.groupby("app_version"):
        tot = len(grp)
        neg = len(grp[grp["sentiment"] == "negative"])
        crit = len(grp[grp["severity"] >= 4])
        summary.append({
            "App Version": ver,
            "Sample Size": tot,
            "Avg Rating": f"{grp['star_rating'].mean():.2f} / 5.0",
            "Negative Share": f"{(neg / tot) * 100:.1f}%",
            "Critical Defect Share (4-5)": f"{(crit / tot) * 100:.1f}%",
            "Top Feature Area": grp[grp["severity"] >= 2]["feature_area"].mode()[0] if not grp[grp["severity"] >= 2].empty else "None"
        })

    summary_df = pd.DataFrame(summary)
    print(summary_df.to_string(index=False))

    # Render Visual Dashboard
    sns.set_theme(style="whitegrid", font="sans-serif")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # Panel 1: Rating and Severity by Version
    ver_metrics = sub_df.groupby("app_version").agg(
        avg_rating=("star_rating", "mean"),
        avg_severity=("severity", "mean")
    ).reset_index()

    x = range(len(ver_metrics))
    width = 0.35

    ax1.bar([i - width/2 for i in x], ver_metrics["avg_rating"], width=width, label="Average Star Rating (Higher is better)", color="#2563EB", edgecolor="#1E293B")
    ax1.bar([i + width/2 for i in x], ver_metrics["avg_severity"], width=width, label="Average Severity (Lower is better)", color="#DC2626", edgecolor="#1E293B")

    ax1.set_xticks(x)
    ax1.set_xticklabels(ver_metrics["app_version"], fontsize=11, fontweight="bold")
    ax1.set_title("Quality & Severity Telemetry by App Release", fontsize=13, fontweight="bold", pad=12)
    ax1.set_ylabel("Score (1 to 5)", fontsize=11, fontweight="bold")
    ax1.set_ylim(0, 5.5)
    ax1.legend(loc="upper right")

    # Panel 2: Defect Distribution by Feature Area per Version
    complaints = sub_df[sub_df["severity"] >= 2].copy()
    if not complaints.empty:
        palette = sns.color_palette("tab10", n_colors=len(valid_versions))
        sns.countplot(
            data=complaints,
            y="feature_area",
            hue="app_version",
            ax=ax2,
            palette=palette,
            edgecolor="#1E293B",
            linewidth=0.8
        )
        ax2.set_title("Defect Volume by Feature Area Across Releases", fontsize=13, fontweight="bold", pad=12)
        ax2.set_xlabel("Complaint Count", fontsize=11, fontweight="bold")
        ax2.set_ylabel("")
        ax2.legend(title="App Release")

    plt.suptitle("LLM Review-Insights Miner: Release Regression & Telemetry Monitor", fontsize=15, fontweight="heavy", y=1.02)
    plt.tight_layout()

    plt.savefig(output_chart, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"\n[SAVED] Version trend chart rendered to: {output_chart}\n")


if __name__ == "__main__":
    analyze_version_regressions()
