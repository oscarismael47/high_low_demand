# high_low_demand

This repository hosts a static web application for monitoring electrical consumption issues.

Where to find the app
- `index.html` — main static app entry (root)
- `consumption_issues.json` — dataset used by the app

Quick start (PowerShell)

```powershell
cd d:\python_scripts\git_repo\high_low_demand
python -m http.server 8000

# Then open http://localhost:8000/index.html in your browser
```

Behavior
- Filters: Status, Severity, Type
- Table: lists matching issues
- Details: choose an issue (first option is "None"), view and edit status and solution (saved in memory)
- Export JSON: downloads updated JSON (`consumption_issues_updated.json`) with in-memory changes

Notes
- The original Streamlit Python app was removed and replaced by this static web app. If you need the Python version, recover it from git history.
# high_low_demand

This repository now hosts a static web application for monitoring electrical consumption issues.

Where to find the app
- `web_app/` — static HTML/CSS/JS application. Open `web_app/index.html` via a local HTTP server.
- `consumption_issues.json` — dataset used by the app.

Quick start (PowerShell):

```powershell
cd d:\python_scripts\git_repo\high_low_demand
python -m http.server 8000

# Then open http://localhost:8000/web_app/ in your browser
```

If you need the original Streamlit Python app, recover it from git history (it was intentionally removed).
# high_low_demand