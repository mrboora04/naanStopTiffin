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

*This file was created as part of the June 2026 frontend audit. Revisit when the cook-side app is built out.*
