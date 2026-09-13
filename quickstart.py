"""
Interactive Quickstart CLI Menu for LLM Review-Insights Miner.
Provides a unified, guided interface for running scraping, analysis,
benchmarking, web dashboard, reports, and Git deployment.
"""

import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def print_banner():
    print("""
==================================================================
        🔍 LLM REVIEW-INSIGHTS MINER: QUICKSTART RUNNER           
==================================================================
  Automated Play Store Telemetry & Product Strategy Framework     
  Author: Harshita (harshita-gits)                                
==================================================================
""")


def run_command(cmd_list, desc):
    print(f"\n[RUNNING] {desc}...")
    try:
        subprocess.run(cmd_list, check=True)
        print(f"[SUCCESS] {desc} finished.")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to execute {desc}: {e}")
    except KeyboardInterrupt:
        print("\n[CANCELLED] Operation stopped by user.")


def main():
    while True:
        print_banner()
        print("Choose an action to perform:")
        print("  1. 🚀 Run Full Analysis Pipeline (Scrape, Classify, Visualize)")
        print("  2. 🌐 Launch Streamlit Interactive Web Dashboard")
        print("  3. ⚔️  Run Competitive Benchmark (Uber vs. DoorDash)")
        print("  4. 📈 Run Release Regression & Version Trend Analysis")
        print("  5. 📄 Generate Standalone Executive HTML Report (report.html)")
        print("  6. 🧪 Run Unit & Integration Test Suite")
        print("  7. 🐙 Push Code to GitHub (git push -u origin main)")
        print("  8. ❌ Exit")
        print("------------------------------------------------------------------")

        choice = input("Enter choice (1-8): ").strip()

        if choice == "1":
            app_id = input("Enter Play Store App ID [default: com.ubercab]: ").strip() or "com.ubercab"
            count = input("Number of reviews [default: 300]: ").strip() or "300"
            run_command([sys.executable, "main.py", "--app-id", app_id, "--count", count], "Full Pipeline")

        elif choice == "2":
            print("\nLaunching Streamlit web dashboard at http://localhost:8501 ...")
            print("Press Ctrl+C in terminal when you wish to stop the server.")
            run_command([sys.executable, "-m", "streamlit", "run", "app.py"], "Streamlit Web Dashboard")

        elif choice == "3":
            run_command([sys.executable, "benchmark.py", "--count", "50"], "Competitive Benchmarking")

        elif choice == "4":
            run_command([sys.executable, "trends.py"], "Release Regression Analysis")

        elif choice == "5":
            run_command([sys.executable, "generate_report.py"], "Executive Report Generation")
            report_path = BASE_DIR / "report.html"
            print(f"\n[TIP] Open {report_path} in any browser and press Ctrl+P to save as PDF!")

        elif choice == "6":
            run_command([sys.executable, "-m", "unittest", "discover", "tests"], "Unit Test Suite")

        elif choice == "7":
            run_command(["git", "push", "-u", "origin", "main"], "GitHub Push")

        elif choice == "8":
            print("\nExiting LLM Review-Insights Miner. Happy building!\n")
            break

        else:
            print("\n[WARNING] Invalid choice. Please enter a number between 1 and 8.")

        input("\nPress Enter to return to main menu...")


if __name__ == "__main__":
    main()
