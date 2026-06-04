# Real-Time Stock Market Analysis System - Vercel Deployment Guide

## Pre-Deployment Checklist ✅

- [x] Dependencies installed in virtual environment
- [x] `requirements.txt` updated with compatible versions
- [x] `.streamlit/config.toml` created
- [x] `vercel.json` created
- [x] Runtime Python 3.10 configured

## Deployment Steps

### 1. **Prepare Project**
```bash
# Virtual environment already activated at: stock/Scripts/activate
# All dependencies installed via requirements.txt
```

### 2. **Create Vercel Project**
```bash
# Install Vercel CLI globally (if not already installed)
npm install -g vercel

# Login to Vercel
vercel login

# Deploy project
vercel
```

### 3. **Configure Environment Variables (if needed)**
In Vercel dashboard, add any required environment variables:
- `PYTHONPATH=./`
- `STREAMLIT_SERVER_HEADLESS=true`
- `STREAMLIT_SERVER_PORT=8501`

### 4. **Important Notes**
- **Python Version**: 3.10 (specified in `vercel.json`)
- **Buildtime**: ~5-10 minutes (due to torch installation)
- **Framework**: Streamlit
- **Memory**: May need 3GB+ due to PyTorch dependency

## Vercel Configuration

The `vercel.json` file contains:
- Build command: Installs dependencies from requirements.txt
- Python runtime configuration
- Server settings for Streamlit

## Optimization Tips

1. **Reduce Cold Start**: Consider using Vercel's cache optimization
2. **Monitor Logs**: Check Vercel dashboard for build/runtime errors
3. **Data Files**: If using large model files, configure `.vercelignore`
4. **API Rate Limits**: Monitor yfinance API calls

## Post-Deployment

Your Streamlit app will be live at: `https://your-project-name.vercel.app`

### Testing Deployment
```bash
# View logs
vercel logs your-project-name

# Redeploy if needed
vercel --prod
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Build timeout | PyTorch is large; Vercel may need increased build timeout |
| Memory exceeded | Consider removing unused dependencies or models |
| Import errors | Ensure all imports are available in requirements.txt |
| Streamlit not starting | Check `.streamlit/config.toml` settings |

---
Generated: 2025-06-05
