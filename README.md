# Bulk SMS Campaign Engine

A production-grade bulk SMS automation system built with Python, PostgreSQL, and Django. Handles contact management, message personalization, opt-out filtering, rate-limited delivery via Sparrow SMS, campaign reporting, and a web UI for non-technical users — end to end.

---

## What It Does

Takes a list of contacts from a database, personalizes a message for each one, filters out opted-out numbers, sends via Sparrow SMS at a controlled rate, tracks delivery, logs cost, and generates an HTML report. A Django web UI allows marketing teams to launch and monitor campaigns without touching code.

---

## Pipeline Flow
Contacts DB → Fetch → Normalize & Validate → Opt-out Filter →
Personalize Messages → Queue → Rate Limit (5 SMS/sec) →
Send with Retry (3 attempts) → Track Delivery → Log Campaign → HTML Report

---

## Features

- **Contact validation** — phone normalization for all Nepali NTC/Ncell formats, missing field detection, deduplication
- **Opt-out filtering** — automatically skips opted-out numbers
- **Message personalization** — supports `{owner_name}`, `{business_name}`, `{city}` with clickable insert buttons in UI
- **Segment filtering** — target contacts by city, category, or any DB filter
- **Rate limiting** — enforces 5 SMS/sec to stay within gateway limits
- **Retry logic** — 3 attempts before marking a send as failed
- **Campaign status tracking** — status moves through `draft → running → completed/failed`
- **Delivery tracking** — records `delivered_at` or `failed_at` per message
- **Campaign logging** — tracks total cost, sent, delivered, failed per campaign
- **HTML report** — auto-generated per campaign with delivery rate, cost, per-contact status
- **Gateway abstraction** — swap simulate and Sparrow with one environment variable, no code changes
- **Excel contact import** — bulk import via styled .xlsx template with validation, duplicate detection, city normalization
- **Contact management** — search, filter, edit, deactivate, reactivate contacts from UI
- **Django web UI** — dashboard, campaign launch form, campaign detail view
- **Background execution** — campaigns run in a background thread, UI never blocks
- **Orphaned campaign reset** — any campaigns stuck in running state are reset to failed on server restart

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.13 |
| Database | PostgreSQL 17 |
| DB Driver | psycopg2 |
| Web Framework | Django 6.0 |
| SMS Gateway | Sparrow SMS (Nepal) |
| HTTP Client | requests |
| Config | python-dotenv |

---

## Project Structure
sms_automation/
│
├── config/
│   └── settings.py           # Env vars, DB config, rate limit, SMS cost, gateway mode
│
├── db/
│   ├── connection.py          # PostgreSQL connection
│   └── queries.py             # Fetch contacts, opt-outs, save messages
│
├── engine/
│   ├── contact_fetcher.py     # Fetches contacts with optional filters
│   ├── validator.py           # Phone normalization, deduplication
│   ├── opt_out_checker.py     # Filters opted-out numbers
│   └── message_generator.py  # Personalizes messages, warns if over 160 chars
│
├── job_queue/
│   ├── job_queue.py           # Wraps Python's queue.Queue
│   └── rate_limiter.py        # Enforces 5 SMS/sec
│
├── gateway/
│   ├── base_gateway.py        # Abstract base class
│   ├── simulate_gateway.py    # Hardcoded delivery for testing
│   └── sparrow_gateway.py     # Sparrow SMS API, error handling, timeout
│
├── tracker/
│   ├── delivery_tracker.py    # Sets delivered_at or failed_at in DB
│   └── campaign_logger.py     # Logs cost and campaign summary
│
├── analytics/
│   └── report.py              # Generates HTML report per campaign
│
├── runner/
│   └── campaign_runner.py     # Full pipeline orchestration with retry
│
├── web/                       # Django web UI
│   ├── manage.py
│   ├── sms_web/               # Django project settings
│   └── campaigns/             # Django app
│       ├── models.py          # Campaign, CampaignLog, Contact models
│       ├── views.py           # dashboard, new_campaign, campaign_detail
│       ├── urls.py            # URL routing
│       └── templates/         # base, dashboard, new_campaign, campaign_detail
│
├── tests/
├── reports/                   # Generated HTML reports (gitignored)
├── .env.example
└── requirements.txt

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/sujana-deve/bulk-sms-engine.git
cd bulk-sms-engine
```

### 2. Create and activate virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password

SPARROW_TOKEN=your_sparrow_api_token
SPARROW_SENDER_ID=your_sender_id

GATEWAY_MODE=simulate
SMS_COST_PER_MESSAGE=1.5
RATE_LIMIT_PER_SECOND=5
```

### 5. Set up the database

Run your PostgreSQL schema to create: `contacts`, `opt_outs`, `messages`, `campaigns`, `campaign_logs`.

### 6. Run pipeline directly

```bash
python main.py
```

### 7. Run Django web UI

```bash
cd web
python manage.py runserver
```

Visit `http://127.0.0.1:8000`

---

## Django Web UI

| Page | URL | Description |
|---|---|---|
| Dashboard | `/` | All campaigns with status, stats, cost, auto-refresh when running |
| New Campaign | `/campaigns/new/` | Launch campaign with segment filters and insert field buttons |
| Campaign Detail | `/campaigns/<id>/` | Stats and template for one campaign |
| Contacts | `/contacts/` | Search, filter, edit, deactivate contacts |
| Import Contacts | `/contacts/import/` | Download template, upload filled Excel file |

Campaign status updates automatically. Dashboard refreshes every 5 seconds while a campaign is running.

---

## Gateway: Simulate vs Sparrow

Switch between simulate and live mode with one environment variable — no code changes needed:

```env
# Testing (default)
GATEWAY_MODE=simulate

# Production
GATEWAY_MODE=sparrow
```

Add your Sparrow credentials to `.env` when received:

```env
SPARROW_TOKEN=your_sparrow_api_token
SPARROW_SENDER_ID=your_sender_id
```

Sparrow SMS credentials require sender ID registration (7-10 business days in Nepal).

---

## Known Limitations

| Limitation | Status |
|---|---|
| Sparrow untested with live credentials | Pending credentials |
| No pagination on contacts page | Planned |
| No duplicate campaign prevention | Planned |
| No message preview before launch | Planned |
| Threading used for background tasks | Replace with Celery pre-production |
| No follow-up sequencing | v2 |
| No inbound SMS / response tracking | v2 |
| No webhook triggers | v2 |
| Deployment not done | Running on dev server only |

---

## Roadmap

- [x] Contact validation and normalization
- [x] Opt-out filtering
- [x] Message personalization with insert field buttons
- [x] Segment filtering by city and category
- [x] Rate limiting and retry logic
- [x] Campaign status tracking
- [x] HTML report generation
- [x] Django web UI
- [x] Excel contact import
- [x] Contact management (view, edit, deactivate)
- [x] Dynamic gateway switching via environment variable
- [ ] Pagination on contacts page
- [ ] Duplicate campaign prevention
- [ ] Message preview panel
- [ ] Celery + Redis for production task queue
- [ ] Follow-up sequencing (time-based drip campaigns)
- [ ] Inbound SMS response tracking
- [ ] Server deployment with Gunicorn + Nginx

---

## Requirements
psycopg2-binary
python-dotenv
requests
django
openpyxl

---

## License

Internal use. Not licensed for public distribution.