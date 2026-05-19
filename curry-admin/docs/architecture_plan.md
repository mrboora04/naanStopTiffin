# Curry Admin Blueprint

## 1. Data Model

**9 Core Entities:**

| Entity | Purpose |
|---|---|
| **Member** | Subscribers (active/paused/cancelled/trial) |
| **PricingPlan** | Subscription tiers (veg/non-veg/both, daily/weekly/monthly rates) |
| **Dish** | Menu items with category, dietary type, ingredients |
| **ScheduleDay** | Daily menu (lunch + dinner, veg + non-veg dishes) |
| **Delivery** | Per-member daily delivery tracking with status |
| **TrialRequest** | Prospects requesting a trial meal |
| **Feedback** | Comments, complaints, suggestions with ratings |
| **PilotProgram** | A/B tests for new menus/areas/features |
| **Payment** | Subscription and trial payment records |

**Key TypeScript Types:**
```typescript
type MemberStatus = "active" | "paused" | "cancelled" | "trial";
type DietaryPreference = "veg" | "non-veg" | "vegan";
type DeliveryStatus = "scheduled" | "out-for-delivery" | "delivered" | "failed" | "skipped";
type TrialStatus = "pending" | "scheduled" | "completed" | "declined" | "no-show";
type FeedbackType = "feedback" | "complaint" | "suggestion";
type PilotStatus = "planning" | "active" | "completed" | "cancelled";
```

**Key Fields:**
- **Member:** `id`, `name`, `phone`, `email`, `address`, `memberStatus`, `dietaryPreference`, `planId`, `renewalDate`, `joinDate`, `allergies`, `deliveryNotes`, `emergencyContact`
- **Delivery:** `id`, `memberId`, `date`, `mealType`, `status`, `deliveryTime`, `routeOrder`, `notes`
- **ScheduleDay:** `id`, `date`, `dayOfWeek`, `isHoliday`, `specialNotes`, `lunchVegDishes[]`, `lunchNonVegDishes[]`, `dinnerVegDishes[]`, `dinnerNonVegDishes[]`

---

## 2. Pages to Build

| Route | What It Shows | Key Features |
|---|---|---|
| `/members` | Subscriber table | Search, filter by status/plan, renewal alerts, action buttons |
| `/deliveries` | Daily delivery list | Group by date, status badges, route order, filter by status |
| `/schedule` | Weekly calendar | 7 day cards, lunch/dinner menus, holiday toggle, edit button |
| `/pricing` | Plan cards | Prices per day/week/month, feature lists, active/inactive toggle |
| `/requests` | Trial inbox | Approve/decline/schedule actions, filter by status |
| `/pilot` | Program dashboard | Participant list, timeline, feedback summary |
| `/comments` | Feedback table | Filter by type/status/rating, mark resolved |

---

## 3. API Routes Needed

- `GET/POST    /api/members`
- `GET/PUT/DEL /api/members/[id]`
- `GET/POST    /api/deliveries`
- `GET/PUT/DEL /api/deliveries/[id]`
- `GET/POST    /api/schedule`
- `GET/PUT/DEL /api/schedule/[id]`
- `GET/POST    /api/pricing`
- `GET/PUT/DEL /api/pricing/[id]`
- `GET/POST    /api/requests`
- `GET/PUT/DEL /api/requests/[id]`
- `GET/POST    /api/comments`
- `GET/PUT/DEL /api/comments/[id]`
- `GET/POST    /api/pilot`
- `GET/PUT/DEL /api/pilot/[id]`
- `GET/POST    /api/payments`
- `GET/PUT/DEL /api/payments/[id]`
- `GET         /api/health`
- `GET         /api/dashboard` *(aggregated stats)*

---

## 4. Future Features Roadmap

### Phase 1 (Core, 2-4 weeks):
- Real PostgreSQL connection (swap mocks)
- Auth & admin roles
- Member CRUD forms
- SMS/WhatsApp delivery notifications
- Payment tracking + reminders

### Phase 2 (Growth, 1-2 months):
- Route optimization for deliveries
- Inventory management + auto shopping lists
- Kitchen prep sheets from schedule
- Customer-facing trial booking page
- Automated renewal reminders
- Revenue analytics dashboard

### Phase 3 (Scale, 2-3 months):
- AI menu recommendations from feedback
- Predictive demand forecasting
- Multi-location support
- Driver mobile app
- Customer loyalty program
- QuickBooks integration

### Phase 4 (Platform, 3-6 months):
- White-label for other tiffin businesses
- Home cook marketplace
- Customer nutrition tracking
- Community reviews/ratings
