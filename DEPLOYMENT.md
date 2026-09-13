# ☁️ 1-Click Free Cloud Deployment Guide
## Hosting Your Interactive Dashboard on Streamlit Community Cloud

Streamlit Community Cloud allows you to host your interactive review miner app for free, giving you a shareable public URL (e.g. `https://harshita-review-insights.streamlit.app`) to put directly on your **resume**, **LinkedIn profile**, and **portfolio**.

---

### Step 1: Ensure Your Code is Pushed to GitHub
Make sure your repository has been pushed to:
`https://github.com/harshita-gits/play-store-review-analyzer`

---

### Step 2: Sign Up / Log In to Streamlit Cloud
1. Go to **[share.streamlit.io](https://share.streamlit.io)**.
2. Click **Continue with GitHub** to authenticate with your `@harshita-gits` account.

---

### Step 3: Deploy the Application
1. Click the **"New app"** button in the top right.
2. Fill in the repository details:
   - **Repository**: `harshita-gits/play-store-review-analyzer`
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL** (Optional custom subdomain): `harshita-review-insights.streamlit.app`
3. Click **"Advanced settings..."** (Optional):
   - Under **Secrets**, you can optionally paste your `OPENAI_API_KEY`:
     ```toml
     OPENAI_API_KEY = "sk-your-openai-api-key"
     LLM_MODEL = "gpt-4o-mini"
     ```
   - *(If left blank, the app will run seamlessly in zero-cost heuristic mode!)*
4. Click **Deploy!**

---

### Step 4: Add the Live Link to Your Resume & LinkedIn
Once deployed (typically takes 60–90 seconds), copy your live URL:
```text
🔗 Live Demo: https://harshita-review-insights.streamlit.app
```
Add this link:
1. To your **LinkedIn Case Study post**.
2. Under the project section of your **Resume**.
3. In the "About" website field of your **GitHub repository**.
