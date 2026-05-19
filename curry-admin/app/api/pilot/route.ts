import { NextResponse } from 'next/server';

// Stub — no pilot data in mockData yet
const mockPilotPrograms: { id: string; name: string; status: string; participants: string[]; timeline: string; feedbackSummary: string }[] = [];

export async function GET() {
  return NextResponse.json(mockPilotPrograms);
}

export async function POST(request: Request) {
  const data = await request.json();
  const newItem = { id: Date.now().toString(), participants: [], ...data };
  return NextResponse.json(newItem, { status: 201 });
}
