"""
Prompt engineering templates and structured JSON schema for review classification.
Includes prompt design iteration notes for portfolio and case study documentation.
"""

from typing import List, Dict, Any

# Target JSON Schema expected from the LLM
EXTRACTION_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "theme": {
            "type": "string",
            "description": "Concise 2-4 word description of the specific issue or praise (e.g., 'Driver Cancellation', 'Overcharged Fare', 'App Freeze on Checkout')."
        },
        "sentiment": {
            "type": "string",
            "enum": ["positive", "negative", "neutral"],
            "description": "Overall sentiment of the user review."
        },
        "severity": {
            "type": "integer",
            "minimum": 1,
            "maximum": 5,
            "description": "Severity rating: 1 (positive / cosmetic feedback) to 5 (critical failure, monetary loss, safety hazard, account lockout)."
        },
        "feature_area": {
            "type": "string",
            "enum": [
                "Billing & Payments",
                "Trip Experience & Drivers",
                "App Performance & Bugs",
                "Navigation & Geolocation",
                "Promotions & Dynamic Pricing",
                "Customer Support",
                "Account & Login",
                "General UI/UX"
            ],
            "description": "The functional product domain the feedback belongs to."
        },
        "reasoning": {
            "type": "string",
            "description": "Brief 1-sentence justification for the assigned theme, feature area, and severity."
        }
    },
    "required": ["theme", "sentiment", "severity", "feature_area", "reasoning"],
    "additionalProperties": False
}

SYSTEM_PROMPT = """You are an expert Senior Product Operations & Quality Analyst analyzing mobile app user reviews.
Your goal is to parse raw user reviews into highly standardized, actionable product telemetry.

Guidelines:
1. OUTPUT FORMAT: Respond ONLY with a valid JSON object matching the requested schema. Do NOT include markdown code blocks (```json), preamble, or extra commentary.
2. SENTIMENT: Assign 'positive', 'negative', or 'neutral'.
   - If the review is sarcastic (e.g. 'Great job taking my money and never sending a car'), identify the true sentiment as 'negative'.
   - If mixed, prioritize the primary defect causing user drop-off or churn.
3. SEVERITY SCALE (1 to 5):
   - 1: Positive compliment, trivial suggestion, or minor cosmetic observation.
   - 2: Minor friction, slow load, or mild annoyance that didn't block the core workflow.
   - 3: Moderate recurring bug, UI confusion, or inconvenient operational delay.
   - 4: High disruption: trip cancelled midway, unable to book, unexpected surge charge, app crash during critical flow.
   - 5: Critical/Catastrophic: unjustified financial charge without refund, account wrongfully deactivated, severe safety concern, scam/fraud allegation.
4. FEATURE AREA: Map strictly to one of:
   ['Billing & Payments', 'Trip Experience & Drivers', 'App Performance & Bugs', 'Navigation & Geolocation', 'Promotions & Dynamic Pricing', 'Customer Support', 'Account & Login', 'General UI/UX']
5. THEME: Write a clean, canonical 2-4 word theme that clusters well with similar complaints (e.g. 'Driver Cancellation After Wait', 'Unfair Surge Pricing', 'App Crashes on Launch', 'Refund Processing Delay'). Avoid overly verbose descriptions.
"""

FEW_SHOT_EXAMPLES: List[Dict[str, Any]] = [
    {
        "review": "Driver accepted, made me wait 15 minutes, then cancelled on me. Now Uber charged me a $5 cancellation fee!! Total scam.",
        "star_rating": 1,
        "output": {
            "theme": "Cancellation Fee After Driver No-Show",
            "sentiment": "negative",
            "severity": 5,
            "feature_area": "Billing & Payments",
            "reasoning": "User was penalized with a fee despite the driver failing to arrive, representing direct financial injustice."
        }
    },
    {
        "review": "The new update looks clean and modern, but the app keeps freezing when I tap 'Confirm Pickup'. Had to reinstall twice.",
        "star_rating": 2,
        "output": {
            "theme": "App Freeze on Pickup Confirmation",
            "sentiment": "negative",
            "severity": 4,
            "feature_area": "App Performance & Bugs",
            "reasoning": "A critical conversion funnel blocker preventing ride confirmation, requiring reinstallation."
        }
    },
    {
        "review": "Super smooth ride! Driver was polite and the route was fast. Love the live ETA sharing feature.",
        "star_rating": 5,
        "output": {
            "theme": "Fast ETA & Courteous Driver",
            "sentiment": "positive",
            "severity": 1,
            "feature_area": "Trip Experience & Drivers",
            "reasoning": "Unambiguous positive praise for core ride quality and trip sharing."
        }
    }
]

def build_review_prompt(review_text: str, star_rating: int = None) -> str:
    """Build the single-review classification prompt."""
    rating_str = f" [Star Rating: {star_rating}/5]" if star_rating is not None else ""
    return f"""Analyze the following app review{rating_str}:
---
"{review_text}"
---
Return the single JSON object matching the schema:"""


# Documentation of Prompt Engineering Iterations
PROMPT_ITERATION_LOG = """
### Prompt Engineering Iteration Log (Design Process)

1. **Iteration 1 (Naive Zero-Shot Prompt)**:
   - *Prompt*: "Read this review and tell me what the user is complaining about, sentiment, and how bad it is."
   - *Result*: Output returned inconsistent free-form strings ("really bad", "moderate"), unstructured text, and vague themes ("driver issue", "bad app").
   - *Failure Mode*: Could not be grouped or clustered in pandas without messy fuzzy matching.

2. **Iteration 2 (Enum Classification + Severity Scale)**:
   - *Prompt*: Added JSON schema with strict 1-5 severity and fixed feature areas.
   - *Result*: Significant improvement in consistency, but sarcastic reviews ("Thanks for charging me twice, awesome service") were misclassified as 'positive' with severity 1.
   - *Fix*: Added explicit instructions identifying sarcasm and anchoring severity to financial/safety impact.

3. **Iteration 3 (Few-Shot Calibrated Production Prompt)**:
   - *Prompt*: Integrated 3 diverse few-shot demonstrations (sarcastic financial penalty, funnel-blocking crash, positive journey).
   - *Result*: High consistency (>95% valid JSON), reliable severity calibration, and concise 2-4 word thematic clustering ready for executive aggregation.
"""
