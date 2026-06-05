# Future Plans

## Cook-Side AI Assistant

**Requested:** 2026-06-03  
**Approved by:** User (via audit comment)  
**Status:** 📋 Planned — not yet implemented

---

### Concept

Add an AI-powered floating chat assistant specifically for **cooks** in the kitchen — not customer-facing, not the admin panel.

### Use Cases

1. **Menu questions:** "What are today's vegan orders?"
2. **Delivery status:** "How many deliveries are left in route 3?"
3. **Substitution help:** "Suggest a replacement for paneer today"
4. **Quick counts:** "How many active members have a nut allergy?"

### Proposed Implementation

- **Entry point:** Floating action button (bottom-right, tablet-safe tap size)
- **Interface:** Side drawer or modal with conversation history
- **Backend:** Connects to existing `/api/v1/ai/menu-search` and decision tree endpoints
- **Context:** Auto-injects today's delivery schedule and member dietary preferences
- **Auth:** Cook-level session only — admin panel already has full data access

### Design Notes

- Only for the **cook/kitchen view** — admin panel may not need this
- Streaming responses preferred for a live feel
- Voice input consideration for hands-free use in the kitchen
- Do NOT show this to customers

### Skills to Use at Implementation Time

- `frontend/interactivity-and-feedback/building-ai-chat`
- `backend/ai-ml` for connecting to the existing decision tree

---

## KNN "Lone Bird" Growth Features

**Requested:** 2026-06-05  
**Status:** 📋 Idea Book — strong potential for future app integration

### Concept
Leveraging K-Nearest Neighbors (KNN) to build hyper-personalized discovery and recommendation features for "Lone Birds" (ad-hoc users who order outside of the standard subscription plans).

### Use Cases to Explore
1. **Cook Meal Rotation & Insights (Reverse-KNN):** Grouping the customer base of a specific cook to advise the cook on what to prep next. (e.g., "50% of your audience eats spicy food—add a spicy dish next week"). This guarantees the cook's new menu will sell out.
2. **Budget Discovery Bar:** A filter specifically for student workers. KNN clusters them with cooks and meals that match the historical spending habits of their nearest demographic neighbors.
3. **Seasonal Recommendations:** Recommending new cooks and seasonal schedules based on what similar Lone Bird users are currently exploring.

---

*This file was created as part of the June 2026 frontend audit. Revisit when the cook-side app is built out.*
