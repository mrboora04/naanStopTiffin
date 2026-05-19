"""
NaanStop Tiffin – FastAPI Backend
Entry point: boots the app, registers all routers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from routers import members, deliveries, schedule, pricing, requests, comments, pilot, payments

# ── Create all tables on startup (SQLite / swap to PostgreSQL later) ──
Base.metadata.create_all(bind=engine)

app = FastAPI(title="NaanStop Tiffin API", version="1.0.0")

# ── CORS: allow the Next.js dev server ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──
app.include_router(members.router,   prefix="/api/members",   tags=["Members"])
app.include_router(deliveries.router, prefix="/api/deliveries", tags=["Deliveries"])
app.include_router(schedule.router,  prefix="/api/schedule",  tags=["Schedule"])
app.include_router(pricing.router,   prefix="/api/pricing",   tags=["Pricing"])
app.include_router(requests.router,  prefix="/api/requests",  tags=["Trial Requests"])
app.include_router(comments.router,  prefix="/api/comments",  tags=["Feedback"])
app.include_router(pilot.router,     prefix="/api/pilot",     tags=["Pilot Programs"])
app.include_router(payments.router,  prefix="/api/payments",  tags=["Payments"])


@app.get("/api/health", tags=["Health"])
def health():
    return {"status": "ok"}


@app.get("/api/dashboard", tags=["Dashboard"])
def dashboard_stats():
    """Aggregated dashboard stats – extend as real DB queries later."""
    from database import SessionLocal
    from models import member as m_model, delivery as d_model

    db = SessionLocal()
    try:
        active_members  = db.query(m_model.Member).filter(m_model.Member.member_status == "active").count()
        total_members   = db.query(m_model.Member).count()
        total_deliveries = db.query(d_model.Delivery).count()
        return {
            "activeMembers":   active_members,
            "totalMembers":    total_members,
            "totalDeliveries": total_deliveries,
        }
    finally:
        db.close()
