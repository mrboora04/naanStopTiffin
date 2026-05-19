import { NextResponse } from 'next/server';
import { mockPricing } from '@/lib/mockData';

// Normalise the single pricing object into an array of plans
// This is a stub — replace with real DB query when backend is ready
const plansArray = Object.entries(mockPricing).map(([key, value]) => ({
  id: key,
  ...(typeof value === 'object' && value !== null ? value : { price: value }),
}));

export async function GET() {
  return NextResponse.json(plansArray);
}

export async function POST(request: Request) {
  const data = await request.json();
  const newItem = { id: Date.now().toString(), ...data };
  return NextResponse.json(newItem, { status: 201 });
}
