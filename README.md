# Bulk SMS Campaign Engine

A production-grade bulk SMS automation system built with Python and PostgreSQL. Handles contact management, message personalization, opt-out filtering, rate-limited delivery via Sparrow SMS, and campaign reporting — end to end.

---

## What It Does

Takes a list of contacts from a database, personalizes a message for each one, filters out opted-out numbers, sends via Sparrow SMS at a controlled rate, tracks delivery, logs cost, and generates an HTML report — all from a single command.

The pipeline replaces manual CSV uploads to SMS dashboards with DB-native automation, ICP filtering, and full audit trails.

---

## Pipeline Flow

```
Contacts DB → Fetch → Normalize & Validate → Opt-out Filter →
Personalize Messages → Queue → Rate Limit (5 SMS/sec) →
Send with Retry (3 attempts) → Track Delivery → Log Campaign → HTML Report
```

---

## Features

- **Contact validation** — phone normalization for all Nepali number formats, missing field detection, deduplication
- **Opt-out filtering** — automatically skips numbers that have opted out, no manual management needed
- **Message personalization** — supports `{owner_name}`, `{business_name}`, `{city}` and other contact field variables
- **ICP filtering** — fetch contacts by business type, city, or any DB filter
- **Rate limiting** — enforces 5 SMS/sec to stay within gateway limits
- **Retry logic** — 3 attempts before marking a send as failed
- **Delivery tracking** — records `delivered_at` or `failed_at` per message in the DB
- **Campaign logging** — tracks total cost, sent count, failed count per campaign
- **HTML report** — auto-generated per campaign with delivery rate, cost, and per-contact status
- **Gateway abstraction** — swap between simulate (testing) and Sparrow (production) with one line

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.13 |
| Database | PostgreSQL 17 |
| DB Driver | psycopg2 |
| SMS Gateway | Sparrow SMS (Nepal) |
| HTTP Client | requests |
| Config | python-dotenv |

---

## Project Structure

```
sms_automation/
│
├── config/
│   └── settings.py          # Loads env vars, DB config, rate limit, SMS cost
│
├── db/
│   ├── connection.py         # PostgreSQL connection
│   └── queries.py            # Fetch contacts, fetch opt-outs, save messages
│
├── engine/
│   ├── contact_fetcher.py    # Fetches contacts with optional filters
│   ├── validator.py          # Phone normalization, missing fields, deduplication
│   ├── opt_out_checker.py    # Filters opted-out numbers
│   └── message_generator.py  # Personalizes messages, warns if over 160 chars
│
├── job_queue/
│   ├── job_queue.py          # Wraps Python's queue.Queue
│   └── rate_limiter.py       # Enforces 5 SMS/sec
│
├── gateway/
│   ├── base_gateway.py       # Abstract base class for SMS gateways
│   ├── simulate_gateway.py   # Hardcoded delivery for testing
│   └── sparrow_gateway.py    # Sparrow SMS API with error handling and timeout
│
├── tracker/
│   ├── delivery_tracker.py   # Sets delivered_at or failed_at in DB
│   └── campaign_logger.py    # Logs cost and campaign summary
│
├── analytics/
│   └── report.py             # Generates HTML report per campaign
│
├── runner/
│   └── campaign_runner.py    # Full pipeline orchestration
│
├── tests/                    # Test files
├── reports/                  # Generated HTML reports (gitignored)
├── .env.example              # Environment variable template
└── main.py                   # Entry point
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

Copy `.env.example` to `.env` and fill in your values:

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

SMS_COST_PER_MESSAGE=1.5
RATE_LIMIT_PER_SECOND=5
```

### 5. Set up the database

Run your PostgreSQL schema to create the required tables: `contacts`, `opt_outs`, `messages`, `campaigns`.

### 6. Run

```bash
python main.py
```

Reports are saved to `reports/` as HTML files.

---

## Gateway: Simulate vs Sparrow

For testing, the system uses `simulate_gateway.py` which marks all sends as delivered without hitting any API.

To switch to real Sparrow sends, change one line in `campaign_runner.py`:

```python
# Testing
from gateway.simulate_gateway import SimulateGateway as Gateway

# Production
from gateway.sparrow_gateway import SparrowGateway as Gateway
```

Sparrow SMS credentials require sender ID registration (7-10 business days in Nepal).

---

## Known Limitations

| Limitation | Status |
|---|---|
| No inbound SMS / response tracking | v2 — requires Sparrow inbound SMS setup |
| No follow-up sequencing | v2 — time-based drip sequences planned |
| No web UI | v2 — Django admin portal planned for marketing team access |
| No webhook triggers | v2 — event-based sends require webhook integration |
| Sparrow untested with live credentials | Pending sender ID registration |

---

## Roadmap

- [ ] Follow-up sequencing (time-based drip campaigns)
- [ ] Django admin UI for non-technical users
- [ ] Inbound SMS response tracking via Sparrow
- [ ] Webhook-triggered sends (website visitors, form submissions)
- [ ] Response-aware sequence enrollment

---

## Requirements

```
psycopg2-binary
python-dotenv
requests
```

Generate with:

```bash
pip freeze > requirements.txt
```

---

## License

Internal use. Not licensed for public distribution.