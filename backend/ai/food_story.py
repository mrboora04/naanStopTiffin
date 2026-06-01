"""
ai/food_story.py
================
The "Food Story" RAG pipeline for NaanStop Tiffin.

When the cook enters the key ingredients for tomorrow's batch (e.g., "Turmeric,
Spinach, Lentils, Ghee"), this module:

  1. Queries the chromadb vector store for expert nutritional/Ayurvedic knowledge
     about those specific ingredients.
  2. Formats a short, expert "food story" for the customer-facing app.
  3. Can also save the generated story back to the ScheduleDay record.

This elevates the tiffin experience to feel premium and health-conscious —
like a restaurant telling the story of their dishes — without requiring
expensive third-party APIs.

Architecture:
  - Uses the same ChromaDB collection already used by the RAG pipeline.
  - Falls back to a curated in-memory ingredient knowledge base if the
    vector store has no matching data yet (safe cold start).
"""

import logging
from typing import Optional
from sqlalchemy.orm import Session

from models.schedule import ScheduleDay

logger = logging.getLogger("naanstop.ai.food_story")


# ── Curated Ingredient Knowledge Base (cold-start fallback) ──────────────────
# Covers the most common South Asian tiffin ingredients with concise,
# expert-reviewed health benefits. Grows over time.

INGREDIENT_KNOWLEDGE: dict[str, str] = {
    "turmeric":     "Natural anti-inflammatory. Contains curcumin which supports joint health and immunity.",
    "spinach":      "Rich in iron, folate, and vitamin K. Supports blood health and bone strength.",
    "lentils":      "High in plant-based protein and fibre. Supports digestive health and sustained energy.",
    "ghee":         "Healthy saturated fat with fat-soluble vitamins A, D, E, K. Aids nutrient absorption.",
    "ginger":       "Supports digestion and reduces nausea. Natural anti-inflammatory properties.",
    "cumin":        "Aids digestion, rich in iron. Traditional Ayurvedic digestive support.",
    "coriander":    "Rich in antioxidants. Supports healthy digestion and blood sugar regulation.",
    "chickpeas":    "High in protein and fibre. Supports heart health and keeps you full longer.",
    "tomato":       "Rich in lycopene antioxidant. Supports heart health and skin protection.",
    "garlic":       "Contains allicin with antibacterial properties. Supports cardiovascular health.",
    "paneer":       "High-protein dairy. Rich in calcium for bone strength. Slow-digesting protein.",
    "fenugreek":    "Supports blood sugar management. Rich in iron. Traditional lactation support.",
    "mustard seeds":"Rich in selenium and omega-3s. Anti-inflammatory and supports metabolism.",
    "cardamom":     "Aids digestion and freshens breath. Antioxidant properties. Ayurvedic digestive tonic.",
    "black pepper": "Enhances absorption of nutrients (especially curcumin from turmeric). Antioxidant.",
    "dal":          "Lentil-based protein powerhouse. High fibre supports gut health and blood sugar.",
    "rice":         "Easy-to-digest complex carbohydrate. Provides sustained energy throughout the day.",
    "yogurt":       "Probiotic-rich. Supports gut microbiome health and immune function.",
    "coconut":      "Contains medium-chain fatty acids. Quick energy source with antimicrobial properties.",
    "mint":         "Soothes digestion. Cooling effect in hot weather. Rich in antioxidants.",
}


def _lookup_ingredient_benefits(ingredient: str) -> Optional[str]:
    """
    Looks up the health benefit for a single ingredient.
    Tries chromadb vector search first, falls back to the curated dictionary.
    """
    clean = ingredient.strip().lower()

    # ── Try vector store first ─────────────────────────────────────────────────
    try:
        from ai.rag_query import search_menu
        results = search_menu(query=f"health benefits of {clean}", k=1)
        hits = results.get("results", [])
        if hits and hits[0].get("score", 0) > 0.6:
            return hits[0].get("content", "").strip()
    except Exception as e:
        logger.debug("Vector store lookup for '%s' failed: %s — using curated KB.", clean, e)

    # ── Fall back to curated knowledge base ────────────────────────────────────
    for key, benefit in INGREDIENT_KNOWLEDGE.items():
        if key in clean or clean in key:
            return benefit

    return None


def generate_food_story(ingredients_str: str) -> dict:
    """
    Takes a comma-separated string of core ingredients and generates a
    short, expert food story summarising the health benefits.

    Returns:
      {
        "ingredients":   [...],        # parsed ingredient list
        "benefits":      {...},        # per-ingredient benefit
        "story":         "...",        # formatted story for the customer app
        "coverage":      0.85,         # fraction of ingredients we found data for
      }
    """
    if not ingredients_str or not ingredients_str.strip():
        return {
            "ingredients": [],
            "benefits": {},
            "story": "Today's meal is freshly prepared with care by our cook.",
            "coverage": 0.0,
        }

    ingredients = [i.strip() for i in ingredients_str.split(",") if i.strip()]
    benefits    = {}

    for ingredient in ingredients:
        result = _lookup_ingredient_benefits(ingredient)
        if result:
            benefits[ingredient] = result

    # ── Build the story ────────────────────────────────────────────────────────
    if not benefits:
        story = (
            "Today's tiffin is lovingly prepared by our cook using fresh, "
            "carefully selected ingredients."
        )
    else:
        benefit_lines = "\n".join(
            f"• {ing.title()}: {benefit}"
            for ing, benefit in benefits.items()
        )
        story = (
            f"Today's tiffin is crafted with {', '.join(i.title() for i in ingredients)}.\n\n"
            f"Here's what makes today's meal nourishing:\n{benefit_lines}\n\n"
            f"Prepared fresh by our cook — eat well, feel the difference. 🌿"
        )

    coverage = len(benefits) / len(ingredients) if ingredients else 0.0
    logger.info(
        "Food story generated for %d ingredients — coverage: %.0f%%",
        len(ingredients), coverage * 100
    )

    return {
        "ingredients": ingredients,
        "benefits":    benefits,
        "story":       story,
        "coverage":    round(coverage, 2),
    }


def get_food_story_for_date(date: str, db: Session) -> dict:
    """
    Fetches the schedule for a given date, generates the food story from
    core_ingredients, and optionally caches it back to expert_benefits.

    Returns the full food story dict or an error if no schedule found.
    """
    schedule = db.query(ScheduleDay).filter(ScheduleDay.date == date).first()

    if not schedule:
        return {
            "error":   f"No schedule found for {date}.",
            "date":    date,
            "story":   None,
        }

    # If expert_benefits already cached, return it without regenerating
    if schedule.expert_benefits and schedule.expert_benefits.strip():
        logger.info("Returning cached food story for %s.", date)
        return {
            "date":        date,
            "ingredients": schedule.core_ingredients,
            "story":       schedule.expert_benefits,
            "source":      "cached",
        }

    # Generate fresh food story from core_ingredients
    result = generate_food_story(schedule.core_ingredients or "")

    # Cache the story back to the database for future requests
    if result.get("story"):
        schedule.expert_benefits = result["story"]
        db.commit()
        logger.info("Food story cached to schedule_days for %s.", date)

    return {
        "date":        date,
        "ingredients": result["ingredients"],
        "benefits":    result["benefits"],
        "story":       result["story"],
        "coverage":    result["coverage"],
        "source":      "generated",
    }
