export type MemberStatus = "active" | "paused" | "cancelled" | "trial";
export type DietaryPreference = "veg" | "non-veg" | "vegan";
export type DeliveryStatus = "scheduled" | "out-for-delivery" | "delivered" | "failed" | "skipped" | "pending";

export type TrialStatus = "pending" | "scheduled" | "completed" | "declined" | "no-show";
export type FeedbackType = "feedback" | "complaint" | "suggestion";
export type PilotStatus = "planning" | "active" | "completed" | "cancelled";

export type Member = {
  id: string;
  name: string;
  phone: string;
  email?: string;
  address: string;
  memberStatus: MemberStatus | string;  // allow legacy values like "renewal-due"
  memberType?: string;
  tiffinType?: string;
  dietaryPreference?: DietaryPreference;
  customization?: {
    chapati?: number;
    rice?: boolean;
    notes?: string;
    [key: string]: unknown;
  };
  paymentMethod?: string;
  paymentStatus?: string;
  planId?: string;
  renewalDate: string;
  joinDate?: string;
  joinedDate?: string;
  daysDelivered?: number;
  totalDays?: number;
  allergies?: string;
  deliveryNotes?: string;
  emergencyContact?: string;
};


export type Delivery = {
  id: string;
  memberId: string;
  date: string;
  mealType?: "lunch" | "dinner";
  status: DeliveryStatus;
  deliveryTime?: string;
  routeOrder?: number;
  notes?: string;
  // Extra fields from richer mockData
  memberName?: string;
  address?: string;
  tiffinType?: string;
  customization?: Record<string, unknown>;
  deliveredAt?: string;
};


export type Dish = {
  id: string;
  name: string;
  nameHindi?: string;
  imageUrl?: string;
  category?: string;
  dietaryType?: DietaryPreference;
  ingredients?: string[];

  likes?: number;
  dislikes?: number;
  tags?: string[];
};


export type ScheduleDay = {
  id: string;
  date: string;
  dayOfWeek?: string;
  isHoliday?: boolean;

  specialNotes?: string;
  // Structured fields (full schema)
  lunchVegDishes?: Dish[];
  lunchNonVegDishes?: Dish[];
  dinnerVegDishes?: Dish[];
  dinnerNonVegDishes?: Dish[];
  // Legacy flat fields (used by older mockData)
  vegDishes?: Dish[];
  nonVegDishes?: Dish[];
};


export type PricingPlan = {
  id: string;
  name: string;
  type: "daily" | "weekly" | "monthly";
  dietaryType: "veg" | "non-veg" | "both";
  price: number;
  features: string[];
  isActive: boolean;
};

export type TrialRequest = {
  id: string;
  name: string;
  phone: string;
  address: string;
  status: TrialStatus;
  requestedDate?: string;
  // Extra fields from richer mockData
  email?: string;
  tiffinType?: string;
  customization?: Record<string, unknown>;
  requestedAt?: string;
  sameDay?: boolean;
  nextDay?: boolean;
  assignedDate?: string;
};


export type Feedback = {
  id: string;
  type: FeedbackType;
  rating: number;
  comments: string;
  status: "new" | "resolved";
};

export type PilotProgram = {
  id: string;
  name: string;
  status: PilotStatus;
  participants: string[]; // member ids
  timeline: string;
  feedbackSummary: string;
};

export type Payment = {
  id: string;
  memberId: string;
  amount: number;
  date: string;
  type: "subscription" | "trial";
  status: "success" | "pending" | "failed";
};

// ── Legacy type aliases (used by lib/mockData.ts) ───────────────────────────
/** @deprecated use ScheduleDay */
export type DaySchedule = ScheduleDay;

/** @deprecated use Delivery */
export type DeliveryRecord = Delivery;

/** Pricing tiers */
export type Pricing = {
  monthlyVeg: number;
  monthlyNonVeg: number;
  trialDay: number;
};

