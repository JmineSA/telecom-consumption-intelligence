# Deploying to Streamlit Community Cloud

## Before you push

1. **Make the default data small.** The deployed app loads `modular/assets/default_sample.parquet` on every start.
   Build a whole-customer sample from your full file (keeps each customer's days together):

       python modular/scripts/make_default_sample.py --input data/processed/modelling_dataset.parquet --customers 800

   Expect roughly 5 to 10 MB. Keep the file well under GitHub's 100 MB limit.
2. **Run the tests:** `python -m pytest -q modular/tests`
3. **Check the repo has:** `training/` (the saved model needs it), `models/mobile_data_consumption_pipeline.pkl`, `models/model_info.json`,
   and in `modular/`: `app.py`, `views/`, `src/`, `assets/` (default dataset and reference profile) and `.streamlit/config.toml`.
   Dependencies: Streamlit Cloud reads `requirements.txt` from the repo root or next to the main file, so keep the lines from
   `modular/requirements.txt` in your root `requirements.txt` (or leave that file in `modular/`).

## Deploy

1. Push the project to a public GitHub repository.
2. Sign in at share.streamlit.io with GitHub and choose **Create app**.
3. Pick the repository and branch, and set the main file path to `modular/app.py`.
4. Open **Advanced settings** and choose the same Python version you use locally (3.13).
5. Deploy. The first start takes a few minutes while packages install.

## Settings worth changing for the cloud

- **Upload size:** `.streamlit/config.toml` allows 200 MB, which suits a local machine. On the cloud, set
  `maxUploadSize = 100` or lower, and set the `MAX_UPLOAD_ROWS` environment variable (default 1,000,000 rows).
- **Memory:** a 676,000-row upload used about 0.5 GB once loaded and scored in my test, with a higher peak while
  scoring. Check Streamlit's current resource limits, and lower `MAX_UPLOAD_ROWS` if the app restarts on large files.

## If something goes wrong

| Symptom | Likely cause and fix |
|---|---|
| `ModuleNotFoundError: training` | The `training/` folder is missing from the repo. |
| Warning or error loading the model | scikit-learn version differs from 1.6.1. Keep it pinned in `requirements.txt`. |
| App restarts when a big file is uploaded | Out of memory. Lower `MAX_UPLOAD_ROWS` and `maxUploadSize`. |
| App is slow to open after a quiet spell | Free apps sleep and wake on the first visit. Say so in your README or post. |
| Package install fails | A pinned version is not available for the cloud's Python version. Match the Python version in step 4. |
