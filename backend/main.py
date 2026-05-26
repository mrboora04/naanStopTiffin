"""
NaanStop Tiffin – FastAPI Backend  (v1)
=======================================
Entry point. Boots the application, registers middleware, error handlers,
all routers under /api/v1/, and runs the AI indexing pipeline on startup.

Architecture decisions applied from D:/dev/skills/backend:
  - api-and-communication/implementing-api-patterns:
      • URI versioning  → all routes at /api/v1/*
      • RFC 7807        → global error handlers (middleware/errors.py)
      • Rate limiting   → slowapi token bucket (middleware/rate_limit.py)
      • OpenAPI docs    → enriched metadata, tag descriptions, redoc + swagger
  - ai-infrastructure/ai-data-engineering:
      • sentence-transformers embeddings (free, local, swappable)
      • ChromaDB vector store (persistent, in-process)
      • Auto-indexing on startup if collections are empty
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from database import Base, engine
from middleware.errors import http_exception_handler, validation_error_handler, generic_error_handler
from middleware.rate_limit import limiter
from routers import members, deliveries, schedule, pricing, requests, comments, pilot, payments
from routers import ai as ai_router

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
)
logger = logging.getLogger("naanstop")

# ── Create all SQLite tables on first run ─────────────────────────────────────
Base.metadata.create_all(bind=engine)


# ── Startup / Shutdown lifecycle ───────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs the AI indexing pipeline on startup if the vector store is empty.
    This embeds all schedule days, members, and feedback into ChromaDB so
    the semantic search endpoints are ready immediately.
    """
    try:
        from ai.pipeline import run_all_pipelines, needs_indexing
        from database import SessionLocal

        if needs_indexing():
            logger.info("Vector store is empty — running initial AI indexing pipeline…")
            db = SessionLocal()
            try:
                summary = run_all_pipelines(db)
                logger.info("AI startup indexing complete: %s", summary)
            finally:
                db.close()
        else:
            logger.info("Vector store already populated — skipping startup indexing.")
    except Exception as e:
        # Never block startup because of AI errors
        logger.warning("AI startup indexing skipped due to error: %s", e)

    yield  # ← application runs here

    logger.info("NaanStop Tiffin backend shutting down.")


# ── FastAPI app ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="NaanStop Tiffin API",
    version="1.0.0",
    description="""
## NaanStop Tiffin — Backend API

RESTful API for managing tiffin subscriptions, deliveries, scheduling, and AI-powered
menu search.

### API Versioning
All endpoints are versioned under `/api/v1/`. The `/api/health` endpoint is unversioned
for load balancer compatibility.

### Pagination
All list endpoints use **cursor-based pagination**:
```
GET /api/v1/members?limit=20
→ { "items": [...], "next_cursor": "abc123", "has_more": true }
GET /api/v1/members?cursor=abc123&limit=20  ← next page
```

### Error Format (RFC 7807)
All errors are returned as Problem Details:
```json
{
  "type": "https://naanstop.app/errors/not-found",
  "title": "Not Found",
  "status": 404,
  "detail": "Member 'xyz' not found.",
  "instance": "/api/v1/members/xyz"
}
```

### Rate Limiting
100 requests per minute per IP address. Exceeding returns `429 Too Many Requests`.
""",
    contact={
        "name": "NaanStop Tiffin Operations",
        "email": "ops@naanstop.app",
    },
    license_info={
        "name": "Private — Internal Use Only",
    },
    openapi_tags=[
        {"name": "Members",        "description": "Subscriber management"},
        {"name": "Deliveries",     "description": "Daily delivery records and status tracking"},
        {"name": "Schedule",       "description": "Weekly menu scheduling"},
        {"name": "Pricing",        "description": "Subscription plan tiers and features"},
        {"name": "Trial Requests", "description": "Prospect meal trial management"},
        {"name": "Feedback",       "description": "Member feedback, complaints, and suggestions"},
        {"name": "Pilot Programs", "description": "Pilot / special program management"},
        {"name": "Payments",       "description": "Subscription payment records"},
        {"name": "AI",             "description": "Semantic search, similarity, and delivery prediction"},
        {"name": "Health",         "description": "System health and readiness"},
    ],
    lifespan=lifespan,
)

# ── Rate limiter state ─────────────────────────────────────────────────────────
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# ── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Error handlers (RFC 7807) ──────────────────────────────────────────────────
from fastapi import HTTPException as FastAPIHTTPException

app.add_exception_handler(FastAPIHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(RateLimitExceeded, http_exception_handler)
app.add_exception_handler(Exception, generic_error_handler)

# ── Routers (all under /api/v1/) ───────────────────────────────────────────────
V1 = "/api/v1"

app.include_router(members.router,    prefix=f"{V1}/members",    tags=["Members"])
app.include_router(deliveries.router, prefix=f"{V1}/deliveries", tags=["Deliveries"])
app.include_router(schedule.router,   prefix=f"{V1}/schedule",   tags=["Schedule"])
app.include_router(pricing.router,    prefix=f"{V1}/pricing",    tags=["Pricing"])
app.include_router(requests.router,   prefix=f"{V1}/requests",   tags=["Trial Requests"])
app.include_router(comments.router,   prefix=f"{V1}/comments",   tags=["Feedback"])
app.include_router(pilot.router,      prefix=f"{V1}/pilot",      tags=["Pilot Programs"])
app.include_router(payments.router,   prefix=f"{V1}/payments",   tags=["Payments"])
app.include_router(ai_router.router,  prefix=f"{V1}/ai",         tags=["AI"])


# ── Unversioned endpoints ──────────────────────────────────────────────────────

@app.get("/api/health", tags=["Health"])
def health():
    """Health check — returns ok when the server is running."""
    return {"status": "ok", "version": "1.0.0"}


@app.get("/api/v1/dashboard", tags=["Health"])
def dashboard_stats():
    """
    Aggregated dashboard statistics for the admin home screen.
    Returns live counts from the database.
    """
    from database import SessionLocal
    from models import member as m_model, delivery as d_model

    db = SessionLocal()
    try:
        active_members   = db.query(m_model.Member).filter(m_model.Member.member_status == "active").count()
        total_members    = db.query(m_model.Member).count()
        total_deliveries = db.query(d_model.Delivery).count()
        return {
            "activeMembers":   active_members,
            "totalMembers":    total_members,
            "totalDeliveries": total_deliveries,
        }
    finally:
        db.close()
