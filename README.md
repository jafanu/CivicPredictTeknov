# CIVIC-PREDICT AI

**Predictive Public Service Intelligence Platform**

CIVIC-PREDICT AI is a Generative AI platform that transforms public-service data into predictive insights, risk scores, and actionable recommendations for smarter government decision-making.

> Ventor Team — SMA Islam Al Azhar 4 Bekasi Kemang Pratama
> TEKNOVISTAFEST 2026
> Adil,Firzy,Jaffan

---

## Features

- **Public Service Risk Score** — Every issue scored 0–100 based on complaints, history, severity, and impact
- **Interactive Risk Map** — Geographic visualization with color-coded markers across Greater Jakarta
- **AI Predictions** — Forecast which problems will worsen, recur, or improve
- **AI Recommendations** — Actionable, department-specific next steps
- **AI Assistant** — Chat-based decision support for government officials
- **Advanced Analytics** — Charts, trends, department performance, geographic distribution
- **Demo Mode** — 50 realistic simulated issues across 8 categories and 5 cities

## Tech Stack

| Layer     | Technology                     |
|-----------|--------------------------------|
| Backend   | Flask (Python)                 |
| Database  | SQLite                         |
| Frontend  | Jinja2, Bootstrap 5, Chart.js |
| Map       | Leaflet.js (CartoDB tiles)     |
| Icons     | Font Awesome 6                 |
| Fonts     | Inter (Google Fonts)           |

---

## Quick Start (Local)

```bash
# Clone the repo
git clone https://github.com/your-username/civic-predict-ai.git
cd civic-predict-ai

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

### Demo Accounts (No Password Needed)

| Role                  | Click to Sign In As |
|-----------------------|---------------------|
| Administrator         | `admin`             |
| Government Analyst    | `analyst`           |
| Dinas PUPR            | `pupr`             |
| Dinas Perhubungan     | `dishub`            |
| Dinas Lingkungan Hidup| `lh`               |

---

## Deploy to PythonAnywhere (Free, No Card)

1. Create a free account at [pythonanywhere.com](https://www.pythonanywhere.com)
2. Open a **Bash console** and run:
   ```bash
   git clone https://github.com/your-username/civic-predict-ai.git
   cd civic-predict-ai
   pip install --user -r requirements.txt
   ```
3. Go to **Web** tab → **Add a new web app** → **Manual configuration** → **Python 3.10**
4. Set **Source code:** `/home/yourusername/civic-predict-ai`
5. Under **WSGI configuration file**, click the link to edit it. Replace ALL content with:
   ```python
   import sys, os
   project_home = os.path.expanduser('~/civic-predict-ai')
   if project_home not in sys.path:
       sys.path.insert(0, project_home)
   from app import app as application
   ```
6. Go to **Files** tab → upload or `git pull` the project files
7. Go to **Web** tab → click **Reload**
8. Your app is live at `https://yourusername.pythonanywhere.com`

> The app auto-initializes the database with 50 simulated issues on first boot.

---

## Project Structure

```
civic-predict-ai/
├── app.py              # Flask application (routes + logic)
├── config.py           # Configuration
├── init_db.py          # Database schema + 50 mock issues
├── requirements.txt    # Python dependencies
├── Procfile            # Render deployment config
├── runtime.txt         # Python version
├── index.html          # Static landing page (GitHub Pages)
├── civic_predict.db    # SQLite database (auto-created)
├── static/
│   ├── css/style.css   # Complete design system (4,700+ lines)
│   └── js/app.js       # Interactive features (charts, map, chat)
└── templates/
    ├── base.html        # Base layout (sidebar + top bar)
    ├── landing.html     # Marketing landing page
    ├── login.html       # Role-selection login
    ├── dashboard.html   # Executive dashboard
    ├── risk_map.html    # Interactive Leaflet map
    ├── issues.html      # Filterable issues table
    ├── issue_detail.html # Issue analysis page
    ├── predictions.html  # AI risk predictions
    ├── recommendations.html # AI action recommendations
    ├── ai_assistant.html  # Chat-based AI assistant
    ├── analytics.html    # Charts and analytics
    ├── data_sources.html # Data source status
    ├── reports.html      # Report generator
    └── settings.html     # Platform settings
```

---

## How the Risk Score Works

Each issue is scored **0–100** based on:

| Factor              | Weight |
|---------------------|--------|
| Complaint frequency | +25    |
| Repeated incidents  | +20    |
| Public impact       | +20    |
| Asset condition     | +16    |
| Recent report spike | +10    |
| Recurrence pattern  | +9     |

**Score → Severity:**
- **75–100** → Critical (red)
- **50–74** → High (orange)
- **25–49** → Medium (amber)
- **0–24** → Low (green)

---

## License

This project was created for TEKNOVISTAFEST 2026 by the Ventor Team.
