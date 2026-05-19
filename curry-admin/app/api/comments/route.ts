import { NextResponse } from 'next/server';

// Stub — no feedback data in mockData yet
// Replace with real DB query when backend is ready
const mockFeedback: { id: string; type: string; rating: number; comments: string; status: string }[] = [];

export async function GET() {
  return NextResponse.json(mockFeedback);
}

export async function POST(request: Request) {
  const data = await request.json();
  const newItem = { id: Date.now().toString(), status: 'new', ...data };
  return NextResponse.json(newItem, { status: 201 });
}
