# Tourism Revenue Risk Dashboard

Interactive Streamlit dashboard for a tourism-dependency / Monte Carlo
revenue-risk analysis (162→198 countries), built on top of the modeling
notebook.

- `app.py` — the dashboard (global map, country deep dive, comparisons, data export)
- `scale_pipeline.py` — extends country coverage beyond the strict 162-country
  filter using a tiered fallback approach (run this before deploying if you
  want wider coverage)
- `notebooks/Mini_Project_Part2_Modeling.ipynb` — the full research notebook
  (model backtesting, champion-model selection, Monte Carlo simulation)
- `data/` — CSVs the app reads
- `requirements.txt` — Python dependencies

---

## Two ways to get this on GitHub

**Option A — no git commands at all (recommended if `git push` is fighting you).**
Use GitHub's website to create the repo and drag-and-drop the files in.
See **"Manual, browser-only setup"** below.

**Option B — git command line.** See the "Git command-line setup" section
further down (this is what we tried before).

---

## Manual, browser-only setup (create repo + upload + deploy, all in the browser)

### Step 1 — Create the repository on GitHub
1. Go to **https://github.com/new** (log in first).
2. **Repository name:** `tourism-risk-dashboard`
3. Choose **Public** (required for the free tier of Streamlit Community Cloud
   to deploy it) or Private if you have a paid Streamlit plan.
4. **Do not** check "Add a README file," "Add .gitignore," or "Choose a license."
   Leave the repo completely empty.
5. Click **Create repository**. You'll land on a page with a URL like
   `https://github.com/Jamtsho2004/tourism-risk-dashboard`.

### Step 2 — Upload the files
1. On that empty repo page, click **"uploading an existing file"** (it's a
   link in the middle of the page).
2. Unzip `tourism-risk-dashboard.zip` on your computer first.
3. Drag the **entire contents** of the unzipped folder into the browser
   upload box — `app.py`, `scale_pipeline.py`, `requirements.txt`,
   `README.md`, `.gitignore`, the `data/` folder, the `notebooks/` folder,
   and the `.streamlit/` folder.
   - GitHub's web uploader supports dragging whole folders in most modern
     browsers (Chrome/Edge). If a folder doesn't drag in as a folder, upload
     its files one by one into a subfolder — click "uploading an existing
     file" again and type the folder path (e.g. `data/cleaned_tourism_data_v2.csv`)
     into the file name box before committing.
   - **Important:** the `.streamlit/config.toml` and `.gitignore` files are
     hidden-style files. GitHub's uploader still accepts them by filename —
     just make sure they're included, don't skip them because you can't
     "see" them in a normal file browser (enable "show hidden files" in
     Windows Explorer / Finder first if needed).
4. Scroll down, add a commit message like "Initial dashboard upload," and
   click **"Commit changes."**
5. Refresh the repo page and confirm you see `app.py`, `data/`, `notebooks/`,
   etc. all listed.

### Step 3 — Deploy on Streamlit Community Cloud
1. Go to **https://share.streamlit.io** and sign in with your GitHub account
   (click "Continue with GitHub" and authorize it).
2. Click **"New app"** (or "Create app").
3. Fill in:
   - **Repository:** `Jamtsho2004/tourism-risk-dashboard`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. Click **"Deploy!"** — first build takes 1–3 minutes while it installs
   `requirements.txt` (statsmodels/scikit-learn take the longest).
5. You'll land on your **live public URL**, something like:
   `https://Jamtsho2004-tourism-risk-dashboard-app-xxxxxx.streamlit.app`
6. That's the link you click to see it live. Bookmark it / share it — anyone
   with the link can open it.

### Updating it later
Any time you want to change something: edit the file locally, then on the
GitHub repo page click into that file → the pencil (✏️) **"Edit this file"**
icon → make your change → **"Commit changes."** Streamlit Cloud detects the
new commit and redeploys automatically within a minute or two — no need to
touch Streamlit Cloud again.

---

## Git command-line setup

## Step 1 — Run it locally first

```bash
# 1. Create and activate a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional but recommended) scale up country coverage
python scale_pipeline.py
# This creates data/full_scale_ALLcountry_risk.csv (198 countries instead of 162).
# app.py automatically uses this file if it exists, else falls back to the
# original 162-country file.

# 4. Run the dashboard
streamlit run app.py
```

Open the URL Streamlit prints (usually `http://localhost:8501`). Confirm the
map, country deep-dive, and comparison tabs all load with data before you
move to deployment.

---

## Step 2 — Put the project on GitHub

```bash
# From inside the tourism-risk-dashboard/ folder:
git init
git add .
git commit -m "Tourism revenue risk dashboard"

# Create a new EMPTY repo on github.com first (no README/license), then:
git branch -M main
git remote add origin https://github.com/Jamtsho2004/tourism-risk-dashboard.git
git push -u origin main
```

If you don't have Git set up yet:

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

**Note on data size:** your `cleaned_tourism_data_v2.csv` is ~760 KB, well
under GitHub's limits, so a plain `git add data/` is fine. If you later add
much larger files (>50 MB), use [Git LFS](https://git-lfs.com/) instead.

---

## Step 3 — Deploy on Streamlit Community Cloud (free)

1. Go to **https://share.streamlit.io** and sign in with your GitHub account.
2. Click **"New app"**.
3. Fill in:
   - **Repository:** `Jamtsho2004/tourism-risk-dashboard`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. Click **"Deploy"**. First build takes 1–3 minutes (installing
   `requirements.txt`).
5. You'll get a public URL like:
   `https://Jamtsho2004-tourism-risk-dashboard-app-xxxxxx.streamlit.app`

That URL is your live dashboard — share it directly.

### Updating the live app
Any time you `git push` new commits to `main`, Streamlit Cloud
auto-redeploys within a minute or two. No manual redeploy step needed.

### If the build fails
- Check the **"Manage app" → logs** panel in Streamlit Cloud for the exact
  error.
- Most common cause: a package version mismatch. Pin exact versions in
  `requirements.txt` if needed, e.g. `pandas==2.2.2`.
- `statsmodels` and `scikit-learn` can be slow to build on the free tier —
  this is normal, just wait for the first deploy.

---

## Step 4 — (Optional) Add more real-world data instead of just relaxing filters

Right now `scale_pipeline.py` gets you from 162 → 198 countries by fitting
*simpler* models on *less* data for the harder countries. That's a coverage
trick, not new information. To genuinely scale further:

- **Get longer/cleaner source series.** The 18 countries `scale_pipeline.py`
  still excludes (e.g. Somalia, Kosovo, Turkmenistan) fail because the World
  Bank source data itself has near-total gaps or zero/negative values for
  them — no amount of modeling fixes that. Look for an alternative source
  (e.g. UNWTO, national tourism boards) for just those countries.
- **Add exogenous regressors** (oil-price exposure, visa-openness index,
  flight-connectivity data) to make the risk model more than a receipts-only
  time series — this is a modeling upgrade, not a coverage one, but it's the
  natural "next step up" once coverage is solved.
- **Re-run `scale_pipeline.py`** whenever `cleaned_tourism_data_v2.csv` is
  refreshed with a newer year of data — it's idempotent and safe to re-run.

---

## Project structure

```
tourism-risk-dashboard/
├── app.py                     # Streamlit dashboard
├── scale_pipeline.py          # Country-coverage scaling script
├── requirements.txt
├── .gitignore
├── .streamlit/
│   └── config.toml            # Theme
└── data/
    ├── cleaned_tourism_data_v2.csv
    ├── full_scale_162country_risk.csv
    ├── full_scale_ALLcountry_risk.csv   # created by scale_pipeline.py
    ├── multi_country_risk_comparison.csv
    └── thailand_revenue_risk_forecast.csv
```
