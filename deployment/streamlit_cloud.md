# Streamlit Cloud Deployment Guide

This document explains how to deploy the **Real-Time Stock Market Analysis & Prediction System**
on **Streamlit Cloud**.

---

## 1. Push Project to GitHub

Ensure your repository contains:
- `dashboard/app.py`
- `requirements.txt`
- `modules/`
- `data/` (can be empty)
- `deployment/` (optional)

Commit and push:
```bash
git add .
git commit -m "Deploy Streamlit stock prediction app"
git push origin main

## 2. Create a Streamlit Cloud App

1. Go to https://share.streamlit.io and sign in with GitHub.
2. Click **New app** → select your repository → branch `main` → main file `dashboard/app.py`.
3. Set the Python version / secrets if needed (see next section).

## 3. Environment Variables & Secrets

If your app requires API keys (Alpha Vantage, other services), add them as secrets in Streamlit Cloud:

1. In your Streamlit app dashboard, open **Settings** → **Secrets**.
2. Add keys as `KEY=value` pairs.

Example:

```
ALPHA_VANTAGE_API_KEY="your_key"
OTHER_SERVICE_TOKEN="token"
```

In your code, access secrets with `st.secrets` or environment variables.

## 4. Local Testing

Before pushing, test locally:

```bash
pip install -r requirements.txt
streamlit run dashboard/app.py
```

## 5. Auto Deploy on Push

Streamlit Cloud automatically deploys when you push to the branch configured for the app. After the first deploy, subsequent pushes will trigger rebuilds.

## 6. Troubleshooting

- If a package fails to install, pin a compatible version in `requirements.txt`.
- If the app crashes, check the Streamlit Cloud logs for stack traces and missing secrets.

---

If you want, I can create a `.streamlit/config.toml` to ensure server settings for local Docker/hosting compatibility.
