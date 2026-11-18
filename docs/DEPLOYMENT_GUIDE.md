# DEPLOYMENT GUIDE
## PRESSURE-X 2.0 | SupeRR Selector Season 2 — IPL 2027

---

## 1. DEPLOYMENT PLATFORM

**Primary:** Streamlit Community Cloud (share.streamlit.io)  
**Alternative:** Any Docker-compatible hosting (Railway, Render, Fly.io, AWS ECS)

---

## 2. REPOSITORY STRUCTURE FOR DEPLOYMENT

```
SupeRR-Selector-2027/
├── app.py                 # Entry point (Streamlit expects this)
├── requirements.txt       # Python dependencies
├── .gitignore            # Excludes secrets, cache, venv
├── .env.example          # Template for environment variables
├── data/                 # All datasets (raw, processed, reference)
├── models/               # Core model implementations
├── src/                  # Pipeline, cleaning, scoring, AI
├── dashboard/            # Streamlit pages, components, charts
├── outputs/              # Official rankings + supporting evidence
├── docs/                 # Documentation
└── assets/               # RR logo
```

---

## 3. REQUIRED SECRETS (Streamlit Cloud)

Configure in **Settings → Secrets** (TOML format):

```toml
# Optional: Backboard API for AI Scouting Assistant
BACKBOARD_API_KEY = "espr_xxxxxxxxxxxxxxxxxxxxxxxx"

# Optional overrides (defaults shown)
# BACKBOARD_BASE_URL = "https://app.backboard.io/api"
# BACKBOARD_PROVIDER = "google"
# BACKBOARD_MODEL_NAME = "gemini-2.5-pro"
```

**Note:** Application works fully without `BACKBOARD_API_KEY` (deterministic fallback).

---

## 4. LOCAL DEVELOPMENT SETUP

```bash
# 1. Clone repository
git clone <repo-url>
cd SupeRR-Selector-2027

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy environment template
cp .env.example .env
# Edit .env with your BACKBOARD_API_KEY if available

# 5. Run pipeline validation (optional)
python -m src.pipeline

# 6. Start dashboard
streamlit run app.py
```

Access at `http://localhost:8501`

---

## 5. STREAMLIT COMMUNITY CLOUD DEPLOYMENT

### One-Click Deploy
1. Push repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **"New app"**
4. Select repository, branch `main`/`master`, file `app.py`
5. Add secrets (see Section 3)
6. Click **"Deploy"**

### GitHub Actions (Optional)
Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy to Streamlit Cloud
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Streamlit
        uses: streamlit/deploy-action@v1
        with:
          app-path: app.py
          # Secrets configured in Streamlit Cloud dashboard
```

---

## 6. RUNTIME CONFIGURATION

| Setting | Value | Notes |
|---------|-------|-------|
| Python | 3.11+ | Tested on 3.11.9 |
| Memory | 2 GB+ | Datasets ~70 MB loaded |
| Port | 8501 (default) | Streamlit default |
| Startup time | ~15-30s | Data loading + caching |

---

## 7. ENVIRONMENT VARIABLES

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `BACKBOARD_API_KEY` | No | — | Enables AI Scouting Assistant |
| `BACKBOARD_BASE_URL` | No | `https://app.backboard.io/api` | API endpoint |
| `BACKBOARD_PROVIDER` | No | `google` | LLM provider |
| `BACKBOARD_MODEL_NAME` | No | `gemini-2.5-pro` | Model name |

---

## 8. DATA FILES — NO EXTERNAL DOWNLOADS REQUIRED

All datasets are committed to the repository:
- `data/raw/` — 6 source CSVs (~50 MB)
- `data/processed/` — 11 feature tables (~25 MB)
- `data/reference/` — 1 reference CSV (~5 KB)
- `outputs/official_reference/` — 3 final ranking CSVs (~3 KB)

**No external data fetching at runtime.** All data loads from local paths via `src/utilities/paths.py`.

---

## 9. HEALTH CHECKS

After deployment, verify:

1. **Homepage loads** — Executive Overview (Page 1) renders
2. **All 10 pages accessible** — Navigation sidebar works
3. **Data loads** — Scouting Explorer shows 311 players
4. **Filters work** — Role, nationality, age, score filters
5. **Dynamic Ranking** — Weight sliders recalculate in real-time
6. **RR Squad** — 19 retained players displayed
7. **Charts render** — Plotly interactive charts on all pages
8. **Downloads work** — CSV export buttons functional
9. **AI Assistant** — Falls back gracefully if no API key

---

## 10. TROUBLESHOOTING

| Issue | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError` | Missing dependency | Verify `requirements.txt` installed |
| `FileNotFoundError` | Data path mismatch | Check `src/utilities/paths.py` resolution |
| `KeyError: 'nationality'` | RR squad schema | Ensure `data/reference/rr_current_squad.csv` has `nationality` column |
| AI Assistant shows "Unconfigured" | No API key | Add `BACKBOARD_API_KEY` to secrets |
| Slow startup | Large datasets | First run caches data; subsequent runs faster |
| Memory error | Insufficient RAM | Increase to 2 GB+ |

---

## 11. SUPPORT

- **Repository:** GitHub Issues
- **Backboard SDK:** `pip install backboard-sdk` / Backboard docs
- **Streamlit Cloud:** Streamlit Community Forum