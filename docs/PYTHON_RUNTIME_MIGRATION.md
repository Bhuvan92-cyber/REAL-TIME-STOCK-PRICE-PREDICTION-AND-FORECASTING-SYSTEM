# Python runtime migration

The preferred runtime is **Python 3.12**, recorded in `.python-version`,
Docker images, and GitHub Actions. The application dependency set is CPU-only
by default; PyTorch, torchvision, torchaudio, and Transformers are optional
under the `ml_cpu` extra in `setup.py`.

FastAPI `0.162.0` declares compatibility with Starlette `1.0.1`; both are
pinned consistently in the requirements files. NumPy, pandas, scikit-learn,
statsmodels, yfinance, PyJWT, Streamlit, and Uvicorn are pinned to versions
installable on Python 3.12.

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pytest -m "not live_external"
```

The current workstation only has Python 3.10, so Python 3.12 installation and
runtime execution remain CI/Docker verification items until a 3.12 interpreter
is installed locally.
