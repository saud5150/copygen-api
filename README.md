# CopyGen API

**AI-powered marketing copy generation at API speed.**

Generate high-converting, platform-specific marketing copy in seconds. CopyGen takes your product details, understands your audience, and returns three distinct copy variations — each scored on persuasion effectiveness — so you ship better campaigns, faster.

---

## Results

| Metric | Manual Copywriting | CopyGen API |
|---|---|---|
| Time to 3 variations | ~45 minutes | **~15 seconds** |
| Speed improvement | baseline | **3x faster** |
| Variations per request | 1 (then revise) | **3 unique angles** |
| Platform formatting | manual lookup | **auto-applied** |
| Persuasion scoring | subjective | **algorithmic, 0-100** |

> "3x faster copy generation vs manual writing — with built-in quality scoring."

---

## How It Works

```
POST /api/v1/generate/
```

Send your product details. Get back three scored variations, tuned for your target platform.

**Request:**
```json
{
  "product_name": "FocusFlow",
  "product_description": "A productivity app that uses AI-generated focus sessions, ambient soundscapes, and smart break reminders to help remote workers maintain deep focus for 4+ hours.",
  "target_audience": "Remote software engineers aged 25-35 who struggle with context switching",
  "tone": "casual",
  "platform": "instagram",
  "session_id": "user-abc-12345678"
}
```

**Response:**
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "session_id": "user-abc-12345678",
  "product_name": "FocusFlow",
  "platform": "instagram",
  "tone": "casual",
  "variations": [
    {
      "copy": "Your code doesn't write itself during meetings. 🎯\n\nFocusFlow builds you a fortress of deep work — AI-tuned focus sessions, ambient sound that actually helps, and break reminders that know when you're in the zone.\n\n4+ hours of real focus. Every single day.\n\nTry it free → link in bio\n\n#DeepWork #RemoteLife #DevTools",
      "persuasion_score": 82.4
    },
    {
      "copy": "Context switching is killing your best work.\n\nFocusFlow uses AI to craft focus sessions around YOUR rhythm — with soundscapes that block distractions and breaks timed to your flow state.\n\nRemote devs are shipping 2x more. Join them.\n\nStart your free trial 👇\n\n#ProductivityHack #RemoteWork #FocusMode",
      "persuasion_score": 78.1
    },
    {
      "copy": "What if your work environment adapted to you?\n\nFocusFlow learns when you focus best, wraps you in the right sounds, and keeps you locked in for hours — not minutes.\n\nBuilt for devs who refuse to settle for scattered days.\n\nGet FocusFlow free → link in bio\n\n#WorkSmarter #DevProductivity #FlowState",
      "persuasion_score": 71.6
    }
  ],
  "model_used": "llama-3.3-70b-versatile",
  "latency_ms": 820,
  "created_at": "2026-02-23T08:15:30.123456Z"
}
```

---

## API Reference

### Generate Copy
```
POST /api/v1/generate/
```

| Field | Type | Required | Constraints |
|---|---|---|---|
| `product_name` | string | yes | 2-200 characters |
| `product_description` | string | yes | 10-2000 characters, min 3 words |
| `target_audience` | string | yes | 5-300 characters |
| `tone` | string | yes | `professional`, `casual`, `urgent`, `witty`, `inspirational` |
| `platform` | string | yes | `instagram`, `linkedin`, `google_ad`, `email_subject`, `facebook`, `twitter` |
| `session_id` | string | yes | 8-64 characters |

### Generation History
```
GET /api/v1/history/?session_id=<session_id>
```
Returns paginated list of past generations for a session.

### Generation Detail
```
GET /api/v1/history/<uuid>/
```
Returns the full generation record including all variations.

### Health Check
```
GET /api/v1/health/
```

---

## Persuasion Scoring

Every variation receives a **0-100 persuasion score** computed from seven weighted signals:

| Signal | Weight | What it measures |
|---|---|---|
| CTA strength | 25% | Presence and quality of call-to-action |
| Power words | 15% | Density of high-impact persuasion words |
| Emotional resonance | 15% | Emotional trigger word usage |
| Urgency cues | 10% | Time-sensitive and scarcity language |
| Platform fit | 15% | Length and format match for target platform |
| Readability | 10% | Sentence rhythm and variety |
| Social proof | 10% | Trust signals and proof patterns |

---

## Rate Limiting

Free tier: **10 requests per day** per IP address. Exceeding the limit returns `429 Too Many Requests` with a `retry_after_seconds` field.

---

## Tech Stack

- **Runtime:** Python 3.12, Django 5.1, Django REST Framework
- **Database:** PostgreSQL with connection pooling
- **AI:** Groq (Llama 3.3 70B) — free tier, OpenAI-compatible API
- **Deployment:** Railway / Render with Gunicorn + WhiteNoise
- **Observability:** Structured logging, request timing middleware

---

## Setup

### Prerequisites
- Python 3.12+
- PostgreSQL 15+
- Groq API key (free at [console.groq.com](https://console.groq.com))

### Local Development

```bash
# Clone and enter the project
cd copygen

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run migrations
python manage.py migrate

# Start the server
python manage.py runserver
```

### Deploy to Railway

1. Push to a GitHub repository
2. Connect the repo in [Railway](https://railway.app)
3. Add a PostgreSQL plugin — `DATABASE_URL` is injected automatically
4. Set environment variables in the Railway dashboard:
   - `DJANGO_SECRET_KEY` — generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
   - `DJANGO_ALLOWED_HOSTS` — your Railway domain
   - `GROQ_API_KEY` — your Groq key (free at [console.groq.com](https://console.groq.com))
5. Deploy. The `release` command in `Procfile` handles migrations and static files.

### Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `DJANGO_SECRET_KEY` | yes (prod) | dev fallback | Django secret key |
| `DATABASE_URL` | yes (prod) | localhost | PostgreSQL connection string |
| `GROQ_API_KEY` | yes | — | Groq API key ([free](https://console.groq.com)) |
| `GROQ_MODEL` | no | `llama-3.3-70b-versatile` | Model identifier |
| `GROQ_MAX_TOKENS` | no | `2048` | Max response tokens |
| `GROQ_TEMPERATURE` | no | `0.8` | Sampling temperature |
| `FREE_TIER_RATE_LIMIT` | no | `10/day` | Throttle rate |
| `DJANGO_DEBUG` | no | `False` | Debug mode |
| `DJANGO_ALLOWED_HOSTS` | no | `localhost,127.0.0.1` | Comma-separated hosts |
| `CORS_ALLOWED_ORIGINS` | no | — | Comma-separated origins |
| `LOG_LEVEL` | no | `INFO` | Logging level |

---

## Project Structure

```
copygen/
├── copygen/                  # Django project config
│   ├── settings.py           # All settings, env-driven
│   ├── urls.py               # Root URL routing
│   ├── wsgi.py
│   └── asgi.py
├── generator/                # Core application
│   ├── models.py             # CopyGeneration model
│   ├── views.py              # API endpoints
│   ├── serializers.py        # Request/response validation
│   ├── urls.py               # App URL routing
│   ├── throttling.py         # Daily rate limiter
│   ├── exceptions.py         # Custom error handler
│   ├── middleware.py          # Request logging
│   ├── admin.py              # Admin interface config
│   └── services/
│       ├── prompt_engine.py   # System + user prompt construction
│       ├── scoring.py         # Persuasion heuristic (7 signals)
│       └── openai_client.py   # Groq/OpenAI-compatible integration + parsing
├── manage.py
├── requirements.txt
├── Procfile                  # Railway/Render deploy commands
├── railway.json              # Railway build config
├── runtime.txt               # Python version pin
├── .env.example
└── .gitignore
```

---

## License

MIT
