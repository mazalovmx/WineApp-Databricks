# WineApp

A pure Python web app for finding daily best wine deals — no Databricks required.

## Overview

A lightweight FastAPI application that aggregates and displays wine deals. Built for everyday use by wine enthusiasts who want to quickly browse today's best prices.

## Tech Stack

- **Python 3.10+**
- **FastAPI** — async web framework
- **Jinja2** — HTML templating
- **Pydantic** — data validation
- **HTTPX** — async HTTP client
- **SQLite** — local deal storage (via `aiosqlite`)
- **Uvicorn** — ASGI server

## Quick Start

```bash
# Create a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
uvicorn app.main:app --reload
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

## Project Structure

```
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application entry point
│   ├── config.py         # App configuration
│   ├── models.py         # Pydantic models
│   ├── database.py       # SQLite database layer
│   ├── services.py       # Wine deal fetching / business logic
│   ├── static/
│   │   └── style.css     # Stylesheet
│   └── templates/
│       └── index.html    # Main page template
├── tests/
│   ├── __init__.py
│   └── test_app.py       # Application tests
├── requirements.txt
└── README.md
```

## Running Tests

```bash
pytest tests/ -v
```

## License

MIT
