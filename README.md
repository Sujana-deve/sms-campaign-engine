# Bulk SMS Campaign Engine

A production-grade bulk SMS automation system built with Python, Django, PostgreSQL, and Celery + Redis. Handles contact management, message personalization, opt-out filtering, prepaid balance/billing, rate-limited delivery, background campaign queuing, campaign reporting, and a web UI for non-technical users — end to end.

---

## What It Does

Takes a list of contacts from a database, personalizes a message for each one, filters out opted-out numbers, checks and deducts from a prepaid balance, queues the send as a background task, delivers via a pluggable SMS gateway at a controlled rate, tracks delivery, logs cost, and generates an HTML report. A Django web UI allows marketing teams to launch and monitor campaigns without touching code — and multiple campaigns can be queued back-to-back without blocking each other or the web server.

---

## Pipeline Flow

```
Contacts DB → Fetch → Normalize & Validate → Opt-out Filter →
Personalize Messages → Balance Check & Deduct → Queue (Celery) →
Rate Limit → Send with Retry (3 attempts) → Track Delivery →
Log Campaign → HTML Report
```

---

## Features

- **Contact validation** — phone normalization for Nepali NTC/Ncell formats, missing field detection, deduplication
- **Opt-out filtering** — automatically skips opted-out numbers
- **Message personalization** — supports `{owner_name}`, `{business_name}`, `{city}` with clickable insert buttons and a live preview against a real sample contact before launch
- **Segment filtering** — target contacts by city, category, or any DB filter
- **Prepaid balance system** — campaigns are cost-estimated and balance-checked before launch; insufficient balance blocks the launch with a clear error, no partial charges
- **eSewa ePay v2 integration (core)** — HMAC-signed redirect payments, server-side transaction verification; billing-model hookup pending PM decision, live credentials pending merchant KYC
- **Bulk campaign queuing (Celery + Redis)** — campaigns launch as background tasks instead of blocking the web request; multiple campaigns queue and process sequentially; a campaign survives a web server restart mid-send
- **Rate limiting** — enforces a controlled send rate to stay within gateway limits
- **Retry logic** — 3 attempts before marking a send as failed
- **Campaign status tracking** — status moves through `queued → running → completed/failed`, reflected live on the dashboard with auto-refresh
- **Delivery tracking** — records `delivered_at` or `failed_at` per message
- **Campaign logging** — tracks total cost, sent, delivered, failed per campaign
- **HTML report** — auto-generated per campaign with delivery rate, cost, per-contact status
- **Gateway abstraction** — swap gateways (NTC primary, Sparrow fallback, Simulate for testing) with one environment variable, no code changes
- **Excel contact import** — bulk import via styled .xlsx template with validation, duplicate detection, city normalization
- **Contact management** — search, filter, paginate, edit, deactivate, reactivate contacts from the UI
- **Django web UI** — dashboard, campaign launch form, campaign detail view, contact list with pagination

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.13 |
| Database | PostgreSQL |
| DB Driver | psycopg2 |
| Web Framework | Django 6.0 |
| Task Queue | Celery |
| Broker / Result Backend | Redis (self-hosted, Docker) |
| SMS Gateway | NTC SMS Alert (primary), Sparrow SMS (fallback) |
| Payments | eSewa ePay v2 |
| HTTP Client | requests |
| Config | python-dotenv |

---

## Project Structure

```
sms_automation/
│
├── config/
│   └── settings.py            # Env vars, DB config, rate limit, SMS cost, gateway mode
│
├── db/
│   └── connection.py           # PostgreSQL connection (fresh connection per call — safe for Celery workers)
│
├── engine/
│   ├── contact_fetcher.py      # Fetches contacts with optional filters
│   ├── validator.py            # Phone normalization, deduplication
│   ├── opt_out_checker.py      # Filters opted-out numbers
│   └── message_generator.py    # Personalizes messages, warns if over 160 chars
│
├── job_queue/
│   ├── job_queue.py            # In-memory job queue for a single campaign's send loop
│   └── rate_limiter.py         # Enforces per-message send rate
│
├── gateway/
│   ├── base_gateway.py         # Abstract base class
│   ├── simulate_gateway.py     # Hardcoded delivery for testing
│   ├── gateway_ntc.py          # NTC SMS Alert — primary, blocked on contract/credentials
│   └── sparrow_gateway.py      # Sparrow SMS API — fallback
│
├── tracker/
│   ├── delivery_tracker.py     # Sets delivered_at or failed_at in DB
│   └── campaign_logger.py      # Logs cost and campaign summary
│
├── analytics/
│   └── report.py               # Generates HTML report per campaign
│
├── runner/
│   └── campaign_runner.py      # Full pipeline orchestration with retry
│
├── web/                        # Django project root
│   ├── manage.py
│   ├── docker-compose.yml      # Redis, self-hosted
│   ├── web/                    # Django project settings
│   │   ├── settings.py
│   │   ├── celery.py           # Celery app config
│   │   └── __init__.py
│   ├── campaigns/              # Django app
│   │   ├── models.py           # Campaign, CampaignLog, Contact models
│   │   ├── views.py            # dashboard, new_campaign, campaign_detail, contact_list, etc.
│   │   ├── tasks.py            # Celery task wrapping campaign_runner
│   │   ├── urls.py
│   │   └── templates/
│   └── payments/                # Django app
│       ├── esewa.py            # eSewa signature, redirect, verification core
│       ├── models.py           # Balance, Transaction
│       ├── views.py
│       └── templates/
│
├── reports/                    # Generated HTML reports (gitignored)
├── .env.example
└── requirements.txt
```

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

GATEWAY_MODE=simulate
SMS_COST_NPR=0.6
SMS_RATE_LIMIT=5

# NTC SMS Alert — primary gateway (fill after contract signing)
NTC_TOKEN=
NTC_SENDER_ID=

# Sparrow — fallback only
SPARROW_TOKEN=
SPARROW_SENDER_ID=

# eSewa ePay v2 — fill after merchant credentials received
ESEWA_PRODUCT_CODE=
ESEWA_SECRET_KEY=
```

### 5. Set up the database

Run migrations to create all Django-managed tables (`contacts`, `campaigns`, `campaign_logs`, `balance`, `transactions`, etc.):

```bash
cd web
python manage.py migrate
```

### 6. Start Redis (via Docker Compose)

```bash
docker compose up -d
```

### 7. Start the Celery worker (separate terminal)

```bash
celery -A web worker --loglevel=info --pool=solo --concurrency=1
```

`--pool=solo` is required on Windows. `--concurrency=1` keeps campaigns processing strictly in order.

### 8. Run the Django web UI (separate terminal)

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000`

All three processes (Redis, Celery worker, Django) need to be running for campaigns to send.

---

## Django Web UI

| Page | URL | Description |
|---|---|---|
| Dashboard | `/` | All campaigns with live status (queued/running/completed/failed), stats, cost, auto-refresh while a campaign is active |
| New Campaign | `/campaigns/new/` | Launch campaign with segment filters, insert-field buttons, and live message preview |
| Campaign Detail | `/campaigns/<id>/` | Stats and template for one campaign |
| Contacts | `/contacts/` | Search, filter, paginate, edit, deactivate contacts |
| Import Contacts | `/contacts/import/` | Download template, upload filled Excel file |

---

## Gateway: Simulate vs NTC vs Sparrow

Switch gateways with one environment variable — no code changes needed:

```env
# Testing (default)
GATEWAY_MODE=simulate

# Production — primary
GATEWAY_MODE=ntc

# Production — fallback
GATEWAY_MODE=sparrow
```

---

## Known Limitations / Open Items

| Item | Status |
|---|---|
| NTC gateway integration | Blocked — contract and API docs pending from NTC (external) |
| `gateway_ntc.py` unconditional `response.json()` call | Known bug — will raise on non-JSON error responses; fix once real NTC docs are available |
| eSewa live payment flow | Code complete, never tested end-to-end — sandbox credentials were dead; production credentials pending merchant KYC |
| eSewa billing model | Pending PM decision — pay-after-send is structurally incompatible with eSewa's redirect flow |
| Per-message retry within a Celery task | Handled via existing `send_with_retry` — not chunked into sub-batches; a worker crash mid-campaign loses that campaign's remaining sends (acceptable at current scale) |
| Cross-campaign gateway rate limiting | Not implemented — campaigns run strictly sequentially instead; revisit if concurrent campaigns are ever needed |
| Deployment | Not done — running on dev machine only |

---

## Roadmap

- [x] Contact validation and normalization
- [x] Opt-out filtering
- [x] Message personalization with insert field buttons and live preview
- [x] Segment filtering by city and category
- [x] Rate limiting and retry logic
- [x] Campaign status tracking (queued/running/completed/failed)
- [x] HTML report generation
- [x] Django web UI
- [x] Excel contact import
- [x] Contact management (view, edit, deactivate)
- [x] Contact list pagination
- [x] Dynamic gateway switching via environment variable
- [x] Prepaid balance system with pre-launch cost check and deduction
- [x] eSewa ePay v2 verification core (signature, redirect, status check)
- [x] Celery + Redis background task queue, replacing thread-based execution
- [x] Bulk campaign queuing — sequential, durable across web server restarts
- [ ] NTC gateway integration (blocked on contract/docs)
- [ ] eSewa live end-to-end test (blocked on credentials)
- [ ] eSewa billing model finalized (blocked on PM decision)
- [ ] Follow-up sequencing (time-based drip campaigns)
- [ ] Inbound SMS response tracking
- [ ] Server deployment with Gunicorn + Nginx

---

## Requirements

```
psycopg2-binary
python-dotenv
requests
django
openpyxl
celery
redis
```

---

## License

Internal use. Not licensed for public distribution.