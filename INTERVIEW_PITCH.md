# 🎯 Interview Pitch & Talking Points
## "Using GenAI / LLM Tools to Validate Solutions & Drive Product Decisions"

Use this guide when interviewing for **Product Manager**, **Product Operations**, **AI/ML Product Lead**, or **Data Science** roles.

---

## 🎙️ The 2-Minute Elevator Pitch (STAR Method)

### 1. Situation & Context
> *"In consumer mobile products operating at scale, product managers often face an overwhelming volume of qualitative user reviews on app stores. Traditional sentiment analysis only gives a surface-level 'positive vs. negative' split, making it impossible to separate cosmetic complaints from catastrophic defects that cause churn and chargebacks."*

### 2. Task
> *"To directly address this, I wanted to build an automated telemetry pipeline that uses modern GenAI and structured LLM prompting to mine real-time reviews, cluster them into standardized functional domains, and prioritize product solutions based on severity and business impact."*

### 3. Action
> *"I designed the **LLM Review-Insights Miner** using Python, `google-play-scraper`, and OpenAI's `gpt-4o-mini`. 
> - First, I engineered a few-shot structured prompt using strict JSON Schema, classifying each review into standardized themes, sentiment, functional feature areas, and a calibrated **severity scale from 1 (cosmetic) to 5 (critical financial/safety defect)**.
> - I built batch-processing with exponential backoff for rate limits and regex-based JSON sanitization.
> - Crucially, instead of sorting by raw complaint count, I formulated a **Severity-Weighted Impact Score** ($Impact = Frequency \times Avg\,Severity$) to prioritize issues where users suffer the most."*

### 4. Result
> *"When running this on 300 recent reviews for Uber, while general UX issues had high volume, our pipeline revealed that **Billing & Payments** and **Customer Support** accounted for over **68% of all critical Level-4 and Level-5 severity defects**. 
> Based on these quantitative findings, I formulated three data-backed product specifications—including a **Zero-Fault Telemetry Engine** to automatically waive cancellation fees when drivers stall, projected to cut fee disputes by 45%. 
> I packaged the pipeline with an interactive Streamlit executive dashboard, a full PRD, and publication-ready charts on GitHub."*

---

## 💡 Anticipated Interview Follow-Up Questions & Model Answers

### Q1: "Why did you formulate a 'Severity-Weighted Impact Score' instead of just prioritizing by highest frequency?"
> **Answer**: *"If you prioritize purely by frequency, you end up optimizing for vocal, low-friction cosmetic items—like 'make the dark mode darker' or minor font preferences. Meanwhile, issues like unauthorized duplicate charges or unfair cancellation fees might occur in fewer total reviews, but every single one of those users gives a 1-star rating and churns. By weighting volume by average severity (1 to 5), we isolate the true high-ROI business levers that protect revenue and customer retention."*

### Q2: "How did you ensure the LLM outputs were reliable, consistent, and didn't hallucinate arbitrary themes?"
> **Answer**: *"I iterated through three prompt engineering phases. In Version 1, open-ended zero-shot prompting led to inconsistent strings and vague labels. In Version 3, I locked down a strict JSON Schema, constrained feature areas to a fixed enum taxonomy, anchored severity levels with explicit operational examples (e.g. monetary loss = 5), and incorporated few-shot demonstrations to handle nuanced sarcasm. This achieved over 95% schema adherence without needing fine-tuning."*

### Q3: "How would you validate and measure the success of your proposed product recommendations in production?"
> **Answer**: *"I structured the PRD around an A/B experimentation framework. For instance, with the Zero-Fault Cancellation engine, we would roll out to 10% of traffic in two pilot metros. Our Primary Metric is Cancellation Fee Dispute Rate (targeting a 45% drop). Our Guardrail Metrics are Driver Partner Net NPS and Driver Earnings, ensuring drivers aren't penalized when traffic delays are legitimate."*

---

## 📋 Quick Cheat Sheet of Key Numbers to Cite
- **300 Reviews Analyzed** (Uber `com.ubercab` via `google-play-scraper`)
- **#1 Issue**: Unresponsive Support (Impact: 56.0, Avg Sev: 4.0/5.0)
- **#2 Issue**: Driver Cancellation Penalties (Impact: 40.0, Avg Sev: 4.0/5.0)
- **#3 Issue**: Double Charges / Unresolved Refunds (Impact: 35.0, Avg Sev: 5.0/5.0)
- **Key Recommendation Impact**: 45% reduction in cancellation disputes, MTTR reduced from 28h to <2h.
