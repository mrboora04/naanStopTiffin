"use client";

import { createContext, useContext, useState, ReactNode } from "react";

type Language = "en" | "hi";

type Translations = {
  dashboard: string;
  members: string;
  deliveries: string;
  schedule: string;
  requests: string;
  pricing: string;
  comments: string;
  pilotLab: string;
  totalMembers: string;
  todaysDeliveries: string;
  todaysRevenue: string;
  newTrialRequests: string;
  renewalAlerts: string;
  renewalDue: string;
  vegMenu: string;
  nonVegMenu: string;
  todaysTiffinSummary: string;
  addMember: string;
  addDish: string;
  search: string;
  all: string;
  monthly: string;
  trial: string;
  active: string;
  inactive: string;
  paid: string;
  unpaid: string;
  markDelivered: string;
  failed: string;
  startRoute: string;
  accept: string;
  decline: string;
  moveToTomorrow: string;
  sameDay: string;
  nextDay: string;
  savePrices: string;
  mostLikedDishes: string;
  mostDislikedDishes: string;
  customizationRequests: string;
  dishLikesDislikes: string;
  viewDetails: string;
  save: string;
  cancel: string;
  confirmRenewal: string;
  delivered: string;
  pending: string;
  monthlyVeg: string;
  monthlyNonVeg: string;
  trialDay: string;
  favoriteDishes: string;
  addCustomDish: string;
  settings: string;
};

const translations: Record<Language, Translations> = {
  en: {
    dashboard: "Dashboard",
    members: "Members",
    deliveries: "Deliveries",
    schedule: "Schedule",
    requests: "Requests",
    pricing: "Pricing",
    comments: "Comments",
    pilotLab: "Pilot Lab",
    totalMembers: "Total Members",
    todaysDeliveries: "Today's Deliveries",
    todaysRevenue: "Today's Revenue",
    newTrialRequests: "New Trial Requests",
    renewalAlerts: "Renewal Alerts",
    renewalDue: "Renewal Due",
    vegMenu: "Veg Menu",
    nonVegMenu: "Non-Veg Menu",
    todaysTiffinSummary: "Today's Tiffin Summary",
    addMember: "Add Member",
    addDish: "Add Dish",
    search: "Search by name or phone...",
    all: "All",
    monthly: "Monthly",
    trial: "Trial",
    active: "Active",
    inactive: "Inactive",
    paid: "Paid",
    unpaid: "Unpaid",
    markDelivered: "Mark Delivered",
    failed: "Failed",
    startRoute: "Start Route",
    accept: "Accept",
    decline: "Decline",
    moveToTomorrow: "Move to Tomorrow",
    sameDay: "Same Day",
    nextDay: "Next Day",
    savePrices: "Save Prices",
    mostLikedDishes: "Most Liked Dishes",
    mostDislikedDishes: "Most Disliked Dishes",
    customizationRequests: "Customization Requests",
    dishLikesDislikes: "Dish Likes/Dislikes",
    viewDetails: "View Details",
    save: "Save",
    cancel: "Cancel",
    confirmRenewal: "Confirm Renewal",
    delivered: "Delivered",
    pending: "Pending",
    monthlyVeg: "Monthly Veg",
    monthlyNonVeg: "Monthly Non-Veg",
    trialDay: "One-Day Trial",
    favoriteDishes: "Favorite Dishes",
    addCustomDish: "Add Custom Dish",
    settings: "Settings",
  },
  hi: {
    dashboard: "डैशबोर्ड",
    members: "सदस्य",
    deliveries: "डिलीवरी",
    schedule: "शेड्यूल",
    requests: "अनुरोध",
    pricing: "मूल्य निर्धारण",
    comments: "टिप्पणियाँ",
    pilotLab: "पायलट लैब",
    totalMembers: "कुल सदस्य",
    todaysDeliveries: "आज की डिलीवरी",
    todaysRevenue: "आज की आय",
    newTrialRequests: "नए ट्रायल अनुरोध",
    renewalAlerts: "नवीनीकरण अलर्ट",
    renewalDue: "नवीनीकरण बाकी",
    vegMenu: "शाकाहारी मेनू",
    nonVegMenu: "मांसाहारी मेनू",
    todaysTiffinSummary: "आज का टिफिन सारांश",
    addMember: "सदस्य जोड़ें",
    addDish: "व्यंजन जोड़ें",
    search: "नाम या फोन से खोजें...",
    all: "सभी",
    monthly: "मासिक",
    trial: "ट्रायल",
    active: "सक्रिय",
    inactive: "निष्क्रिय",
    paid: "भुगतान किया",
    unpaid: "भुगतान बाकी",
    markDelivered: "डिलीवर किया",
    failed: "विफल",
    startRoute: "रूट शुरू करें",
    accept: "स्वीकार",
    decline: "अस्वीकार",
    moveToTomorrow: "कल के लिए",
    sameDay: "आज",
    nextDay: "अगला दिन",
    savePrices: "कीमतें सहेजें",
    mostLikedDishes: "सबसे पसंदीदा व्यंजन",
    mostDislikedDishes: "सबसे कम पसंद व्यंजन",
    customizationRequests: "कस्टमाइज़ेशन अनुरोध",
    dishLikesDislikes: "व्यंजन पसंद/नापसंद",
    viewDetails: "विवरण देखें",
    save: "सहेजें",
    cancel: "रद्द करें",
    confirmRenewal: "नवीनीकरण पुष्टि",
    delivered: "डिलीवर किया",
    pending: "लंबित",
    monthlyVeg: "मासिक शाकाहारी",
    monthlyNonVeg: "मासिक मांसाहारी",
    trialDay: "एक दिन का ट्रायल",
    favoriteDishes: "पसंदीदा व्यंजन",
    addCustomDish: "कस्टम व्यंजन जोड़ें",
    settings: "सेटिंग्स",
  },
};

type LanguageContextType = {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: Translations;
};

const LanguageContext = createContext<LanguageContextType>({
  language: "en",
  setLanguage: () => {},
  t: translations.en,
});

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguage] = useState<Language>("en");

  return (
    <LanguageContext.Provider
      value={{ language, setLanguage, t: translations[language] }}
    >
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  return useContext(LanguageContext);
}
