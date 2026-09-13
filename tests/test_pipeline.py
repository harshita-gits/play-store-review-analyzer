"""
Unit and Integration Tests for LLM Review-Insights Miner.
Validates JSON parsing resilience, heuristic taxonomy matching,
severity calibration, and telemetry aggregation mathematics.
"""

import sys
from pathlib import Path
import unittest
import pandas as pd

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from config import FEATURE_AREAS
from extractor import clean_json_response, offline_heuristic_classifier
from visualize import aggregate_complaints


class TestJsonCleaning(unittest.TestCase):
    """Test resilience of the JSON parser against noisy LLM outputs."""

    def test_clean_direct_json(self):
        raw = '{"theme": "App Crash", "sentiment": "negative", "severity": 4, "feature_area": "App Performance & Bugs", "reasoning": "Crash on launch"}'
        parsed = clean_json_response(raw)
        self.assertEqual(parsed["theme"], "App Crash")
        self.assertEqual(parsed["severity"], 4)

    def test_markdown_wrapped_json(self):
        raw = """```json
        {
            "theme": "Double Charge",
            "sentiment": "negative",
            "severity": 5,
            "feature_area": "Billing & Payments",
            "reasoning": "Charged twice for single trip"
        }
        ```"""
        parsed = clean_json_response(raw)
        self.assertEqual(parsed["severity"], 5)
        self.assertEqual(parsed["feature_area"], "Billing & Payments")

    def test_conversational_wrapped_json(self):
        raw = """Here is the structured analysis of the user review:
        {"theme": "Driver Cancellation", "sentiment": "negative", "severity": 4, "feature_area": "Billing & Payments", "reasoning": "Unfair fee"}
        Hope this is helpful!"""
        parsed = clean_json_response(raw)
        self.assertEqual(parsed["theme"], "Driver Cancellation")

    def test_invalid_json_raises_value_error(self):
        raw = "This is not JSON at all."
        with self.assertRaises(ValueError):
            clean_json_response(raw)


class TestTelemetryClassifier(unittest.TestCase):
    """Validate severity calibration and taxonomy compliance."""

    def test_positive_ride_experience(self):
        text = "Great trip, driver was very courteous and arrived fast!"
        result = offline_heuristic_classifier(text, star_rating=5)
        self.assertEqual(result["sentiment"], "positive")
        self.assertEqual(result["severity"], 1)
        self.assertIn(result["feature_area"], FEATURE_AREAS)

    def test_critical_refund_defect(self):
        text = "I was charged twice and the support refused to issue a refund! Stole my money!"
        result = offline_heuristic_classifier(text, star_rating=1)
        self.assertEqual(result["sentiment"], "negative")
        self.assertEqual(result["severity"], 5)
        self.assertEqual(result["feature_area"], "Billing & Payments")

    def test_driver_cancellation_penalty(self):
        text = "Driver accepted, cancelled after 15 minutes, and I got charged a cancellation fee."
        result = offline_heuristic_classifier(text, star_rating=1)
        self.assertEqual(result["severity"], 4)
        self.assertEqual(result["feature_area"], "Billing & Payments")

    def test_app_crash_defect(self):
        text = "App keeps crashing and freezing every time I try to confirm pickup."
        result = offline_heuristic_classifier(text, star_rating=1)
        self.assertEqual(result["severity"], 4)
        self.assertEqual(result["feature_area"], "App Performance & Bugs")


class TestAggregationMathematics(unittest.TestCase):
    """Validate calculation of severity-weighted impact scores."""

    def test_impact_score_calculation(self):
        sample_records = [
            {"review_id": "1", "theme": "Refund Delay", "feature_area": "Billing & Payments", "severity": 5, "star_rating": 1},
            {"review_id": "2", "theme": "Refund Delay", "feature_area": "Billing & Payments", "severity": 5, "star_rating": 1},
            {"review_id": "3", "theme": "Minor UI Glitch", "feature_area": "General UI/UX", "severity": 2, "star_rating": 3},
            {"review_id": "4", "theme": "Minor UI Glitch", "feature_area": "General UI/UX", "severity": 2, "star_rating": 3},
            {"review_id": "5", "theme": "Minor UI Glitch", "feature_area": "General UI/UX", "severity": 2, "star_rating": 3},
        ]
        df = pd.DataFrame(sample_records)
        summary = aggregate_complaints(df)

        # Refund Delay: 2 reviews * 5.0 severity = 10.0 impact score
        refund_row = summary[summary["theme"] == "Refund Delay"].iloc[0]
        self.assertEqual(refund_row["frequency"], 2)
        self.assertEqual(refund_row["avg_severity"], 5.0)
        self.assertEqual(refund_row["impact_score"], 10.0)

        # Minor UI Glitch: 3 reviews * 2.0 severity = 6.0 impact score
        ui_row = summary[summary["theme"] == "Minor UI Glitch"].iloc[0]
        self.assertEqual(ui_row["frequency"], 3)
        self.assertEqual(ui_row["avg_severity"], 2.0)
        self.assertEqual(ui_row["impact_score"], 6.0)

        # Impact score ranking: Refund Delay (10.0) > Minor UI Glitch (6.0)
        self.assertEqual(summary.iloc[0]["theme"], "Refund Delay")


if __name__ == "__main__":
    unittest.main()
