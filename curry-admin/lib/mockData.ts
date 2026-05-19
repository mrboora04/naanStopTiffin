import {
  Member,
  DaySchedule,
  DeliveryRecord,
  TrialRequest,
  Pricing,
  Dish,
} from "@/types";

// Helper to get dates relative to today
function getDate(daysFromNow: number): string {
  const d = new Date();
  d.setDate(d.getDate() + daysFromNow);
  return d.toISOString().split("T")[0];
}

function getDatetime(hoursAgo: number): string {
  const d = new Date();
  d.setHours(d.getHours() - hoursAgo);
  return d.toISOString();
}

export const mockPricing: Pricing = {
  monthlyVeg: 200,
  monthlyNonVeg: 224,
  trialDay: 12,
};

export const mockMembers: Member[] = [
  {
    id: "m1",
    name: "Priya Sharma",
    phone: "7051234567",
    address: "45 Dunlop St W, Barrie, ON",
    memberType: "monthly-veg",
    tiffinType: "veg",
    customization: { chapati: 6, rice: true, notes: "extra dal please" },
    paymentMethod: "interac",
    paymentStatus: "paid",
    memberStatus: "active",
    joinedDate: getDate(-20),
    renewalDate: getDate(10),
    daysDelivered: 20,
    totalDays: 30,
  },
  {
    id: "m2",
    name: "Rajesh Patel",
    phone: "7059876543",
    address: "120 Bayfield St, Barrie, ON",
    memberType: "monthly-nonveg",
    tiffinType: "nonveg",
    customization: { chapati: 8, rice: true, notes: "" },
    paymentMethod: "cash",
    paymentStatus: "paid",
    memberStatus: "active",
    joinedDate: getDate(-15),
    renewalDate: getDate(15),
    daysDelivered: 15,
    totalDays: 30,
  },
  {
    id: "m3",
    name: "Anita Desai",
    phone: "7052223333",
    address: "88 Collier St, Barrie, ON",
    memberType: "monthly-veg",
    tiffinType: "veg",
    customization: { chapati: 4, rice: false, notes: "no spicy food" },
    paymentMethod: "interac",
    paymentStatus: "unpaid",
    memberStatus: "renewal-due",
    joinedDate: getDate(-28),
    renewalDate: getDate(2),
    daysDelivered: 28,
    totalDays: 30,
  },
  {
    id: "m4",
    name: "Vikram Singh",
    phone: "7054445555",
    address: "200 Essa Rd, Barrie, ON",
    memberType: "monthly-nonveg",
    tiffinType: "nonveg",
    customization: { chapati: 6, rice: true, notes: "extra chicken" },
    paymentMethod: "cash",
    paymentStatus: "paid",
    memberStatus: "active",
    joinedDate: getDate(-10),
    renewalDate: getDate(20),
    daysDelivered: 10,
    totalDays: 30,
  },
  {
    id: "m5",
    name: "Meena Gupta",
    phone: "7056667777",
    address: "55 Anne St S, Barrie, ON",
    memberType: "monthly-veg",
    tiffinType: "veg",
    customization: { chapati: 6, rice: true, notes: "" },
    paymentMethod: "interac",
    paymentStatus: "paid",
    memberStatus: "active",
    joinedDate: getDate(-5),
    renewalDate: getDate(25),
    daysDelivered: 5,
    totalDays: 30,
  },
  {
    id: "m6",
    name: "Suresh Kumar",
    phone: "7058889999",
    address: "300 Mapleview Dr E, Barrie, ON",
    memberType: "monthly-nonveg",
    tiffinType: "nonveg",
    customization: { chapati: 8, rice: true, notes: "less oil" },
    paymentMethod: "cash",
    paymentStatus: "unpaid",
    memberStatus: "renewal-due",
    joinedDate: getDate(-27),
    renewalDate: getDate(3),
    daysDelivered: 27,
    totalDays: 30,
  },
  {
    id: "m7",
    name: "Deepa Nair",
    phone: "7051112222",
    address: "15 Toronto St, Barrie, ON",
    memberType: "trial",
    tiffinType: "veg",
    customization: { chapati: 4, rice: true, notes: "first time trying" },
    paymentMethod: "cash",
    paymentStatus: "unpaid",
    memberStatus: "active",
    joinedDate: getDate(0),
    renewalDate: getDate(0),
    daysDelivered: 0,
    totalDays: 1,
  },
  {
    id: "m8",
    name: "Arjun Reddy",
    phone: "7053334444",
    address: "77 Bradford St, Barrie, ON",
    memberType: "monthly-veg",
    tiffinType: "veg",
    customization: { chapati: 6, rice: false, notes: "extra paneer" },
    paymentMethod: "interac",
    paymentStatus: "paid",
    memberStatus: "active",
    joinedDate: getDate(-22),
    renewalDate: getDate(8),
    daysDelivered: 22,
    totalDays: 30,
  },
  {
    id: "m9",
    name: "Kavita Joshi",
    phone: "7057778888",
    address: "160 Cundles Rd E, Barrie, ON",
    memberType: "monthly-nonveg",
    tiffinType: "nonveg",
    customization: { chapati: 6, rice: true, notes: "" },
    paymentMethod: "interac",
    paymentStatus: "paid",
    memberStatus: "active",
    joinedDate: getDate(-18),
    renewalDate: getDate(12),
    daysDelivered: 18,
    totalDays: 30,
  },
  {
    id: "m10",
    name: "Ravi Malhotra",
    phone: "7059990000",
    address: "42 Kozlov St, Barrie, ON",
    memberType: "trial",
    tiffinType: "nonveg",
    customization: { chapati: 6, rice: true, notes: "" },
    paymentMethod: "cash",
    paymentStatus: "paid",
    memberStatus: "active",
    joinedDate: getDate(0),
    renewalDate: getDate(0),
    daysDelivered: 0,
    totalDays: 1,
  },
];

// Reusable dish data
export const allDishes: Dish[] = [
  { id: "d1", name: "Dal Makhani", nameHindi: "दाल मखनी", imageUrl: "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=400&h=300&fit=crop", likes: 32, dislikes: 2 },
  { id: "d2", name: "Aloo Gobi", nameHindi: "आलू गोभी", imageUrl: "https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=400&h=300&fit=crop", likes: 25, dislikes: 5 },
  { id: "d3", name: "Palak Paneer", nameHindi: "पालक पनीर", imageUrl: "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=400&h=300&fit=crop", likes: 40, dislikes: 1 },
  { id: "d4", name: "Rajma", nameHindi: "राजमा", imageUrl: "https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=400&h=300&fit=crop", likes: 28, dislikes: 3 },
  { id: "d5", name: "Chole", nameHindi: "छोले", imageUrl: "https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=400&h=300&fit=crop", likes: 35, dislikes: 4 },
  { id: "d6", name: "Jeera Rice", nameHindi: "जीरा चावल", imageUrl: "https://images.unsplash.com/photo-1596797038530-2c107229654b?w=400&h=300&fit=crop", likes: 22, dislikes: 1 },
  { id: "d7", name: "Butter Chicken", nameHindi: "बटर चिकन", imageUrl: "https://images.unsplash.com/photo-1603894584373-5ac82b2ae398?w=400&h=300&fit=crop", likes: 45, dislikes: 0 },
  { id: "d8", name: "Chicken Curry", nameHindi: "चिकन करी", imageUrl: "https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=400&h=300&fit=crop", likes: 38, dislikes: 2 },
  { id: "d9", name: "Egg Curry", nameHindi: "अंडा करी", imageUrl: "https://images.unsplash.com/photo-1574484284002-952d92456975?w=400&h=300&fit=crop", likes: 20, dislikes: 6 },
  { id: "d10", name: "Paneer Tikka", nameHindi: "पनीर टिक्का", imageUrl: "https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8?w=400&h=300&fit=crop", likes: 30, dislikes: 2 },
  { id: "d11", name: "Mixed Veg", nameHindi: "मिक्स सब्ज़ी", imageUrl: "https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=400&h=300&fit=crop", likes: 18, dislikes: 8 },
  { id: "d12", name: "Kadhi Pakora", nameHindi: "कढ़ी पकोड़ा", imageUrl: "https://images.unsplash.com/photo-1574484284002-952d92456975?w=400&h=300&fit=crop", likes: 24, dislikes: 3 },
  { id: "d13", name: "Fish Curry", nameHindi: "मछली करी", imageUrl: "https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=400&h=300&fit=crop", likes: 15, dislikes: 7 },
  { id: "d14", name: "Keema Matar", nameHindi: "कीमा मटर", imageUrl: "https://images.unsplash.com/photo-1574484284002-952d92456975?w=400&h=300&fit=crop", likes: 26, dislikes: 4 },
];

export const favoriteDishes: Dish[] = [allDishes[0], allDishes[1], allDishes[2]];

// Categorized dish lists for the schedule dish picker
export const vegDishList: Dish[] = [
  allDishes[0],  // Dal Makhani
  allDishes[1],  // Aloo Gobi
  allDishes[2],  // Palak Paneer
  allDishes[3],  // Rajma
  allDishes[4],  // Chole
  allDishes[5],  // Jeera Rice
  allDishes[9],  // Paneer Tikka
  allDishes[10], // Mixed Veg
  allDishes[11], // Kadhi Pakora
];

export const nonVegDishList: Dish[] = [
  allDishes[6],  // Butter Chicken
  allDishes[7],  // Chicken Curry
  allDishes[8],  // Egg Curry
  allDishes[12], // Fish Curry
  allDishes[13], // Keema Matar
  allDishes[5],  // Jeera Rice (goes with non-veg too)
];

export const mockSchedule: DaySchedule[] = Array.from({ length: 7 }, (_, i) => ({
  id: `sched-${i}`,
  date: getDate(i),
  vegDishes: [
    allDishes[i % 6],
    allDishes[(i + 1) % 6],
    allDishes[5], // Jeera Rice always
  ],
  nonVegDishes: [
    allDishes[6 + (i % 4)],
    allDishes[5], // Jeera Rice
    allDishes[10 + (i % 4)],
  ],
}));

const today = getDate(0);

export const mockDeliveries: DeliveryRecord[] = [
  { id: "del1", memberId: "m1", memberName: "Priya Sharma", address: "45 Dunlop St W, Barrie, ON", tiffinType: "veg", customization: { chapati: 6, rice: true, notes: "extra dal please" }, date: today, status: "pending" },
  { id: "del2", memberId: "m2", memberName: "Rajesh Patel", address: "120 Bayfield St, Barrie, ON", tiffinType: "nonveg", customization: { chapati: 8, rice: true, notes: "" }, date: today, status: "pending" },
  { id: "del3", memberId: "m3", memberName: "Anita Desai", address: "88 Collier St, Barrie, ON", tiffinType: "veg", customization: { chapati: 4, rice: false, notes: "no spicy food" }, date: today, status: "delivered", deliveredAt: new Date().toISOString() },
  { id: "del4", memberId: "m4", memberName: "Vikram Singh", address: "200 Essa Rd, Barrie, ON", tiffinType: "nonveg", customization: { chapati: 6, rice: true, notes: "extra chicken" }, date: today, status: "pending" },
  { id: "del5", memberId: "m5", memberName: "Meena Gupta", address: "55 Anne St S, Barrie, ON", tiffinType: "veg", customization: { chapati: 6, rice: true, notes: "" }, date: today, status: "delivered", deliveredAt: new Date().toISOString() },
  { id: "del6", memberId: "m6", memberName: "Suresh Kumar", address: "300 Mapleview Dr E, Barrie, ON", tiffinType: "nonveg", customization: { chapati: 8, rice: true, notes: "less oil" }, date: today, status: "pending" },
  { id: "del7", memberId: "m8", memberName: "Arjun Reddy", address: "77 Bradford St, Barrie, ON", tiffinType: "veg", customization: { chapati: 6, rice: false, notes: "extra paneer" }, date: today, status: "failed" },
  { id: "del8", memberId: "m9", memberName: "Kavita Joshi", address: "160 Cundles Rd E, Barrie, ON", tiffinType: "nonveg", customization: { chapati: 6, rice: true, notes: "" }, date: today, status: "pending" },
];

export const mockTrialRequests: TrialRequest[] = [
  {
    id: "tr1",
    name: "Sunita Verma",
    phone: "7051119999",
    address: "33 Maple Ave, Barrie, ON",
    tiffinType: "veg",
    customization: { chapati: 4, rice: true, notes: "mild spice please" },
    requestedAt: getDatetime(2), // 2 hours ago
    sameDay: true,
    status: "pending",
  },
  {
    id: "tr2",
    name: "Amit Khanna",
    phone: "7052228888",
    address: "90 Georgian Dr, Barrie, ON",
    tiffinType: "nonveg",
    customization: { chapati: 6, rice: true, notes: "" },
    requestedAt: getDatetime(18), // yesterday evening
    sameDay: false,
    status: "pending",
  },
  {
    id: "tr3",
    name: "Pooja Rao",
    phone: "7053337777",
    address: "12 Lakeshore Dr, Barrie, ON",
    tiffinType: "veg",
    customization: { chapati: 4, rice: false, notes: "gluten sensitive" },
    requestedAt: getDatetime(1), // 1 hour ago
    sameDay: true,
    status: "pending",
  },
];
