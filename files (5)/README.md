# ⚖ Dharma Lens — Legal Intelligence Platform

## Quick Start

```bash
# 1. Install dependencies (once)
pip install -r requirements.txt

# 2. Start server
python3 run.py

# 3. Open browser
http://localhost:5050
```

## File Structure

```
dharma-lens/
├── app.py              ← Flask backend (9 REST endpoints)
├── legal_engine.py     ← NLP classifier + legal content validator
├── run.py              ← One-click launcher
├── requirements.txt    ← Python dependencies
├── static/
│   └── index.html      ← Complete frontend (1540 lines)
└── uploads/            ← Temp folder (auto-cleared after each upload)
```

## Features

- **Upload Case** — PDF/TXT legal documents; validates legal content
- **Scenario Analysis** — Classify any legal situation in plain text
- **Case Insights** — Keyword scores, confidence, acts, articles
- **Case History** — Session-based case storage with delete
- **Knowledge Center** — 8 interactive legal topic cards with search
- **Constitutional Framework** — Interactive domain explorer (8 domains)

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Serve frontend |
| GET | `/api/health` | Server status |
| GET | `/api/categories` | All 8 legal categories |
| POST | `/api/upload` | Upload PDF/TXT for analysis |
| POST | `/api/scenario` | Analyse legal scenario text |
| GET | `/api/cases` | List session cases |
| GET | `/api/case/<id>` | Get single case |
| DELETE | `/api/case/<id>` | Delete case |
| GET | `/api/stats` | Session statistics |

## Requirements

- Python 3.10+
- flask, pdfplumber, pypdf, scikit-learn, numpy, scipy, werkzeug
