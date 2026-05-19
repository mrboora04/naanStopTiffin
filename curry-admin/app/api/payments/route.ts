import { NextResponse } from 'next/server';

// Stub — no payments in mockData yet; replace with real DB query
export async function GET() {
  return NextResponse.json([]);
}

export async function POST(request: Request) {
  const data = await request.json();
  const newItem = { id: Date.now().toString(), ...data };
  return NextResponse.json(newItem, { status: 201 });
}
