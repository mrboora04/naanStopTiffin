import { NextResponse } from 'next/server';
import { mockSchedule } from '@/lib/mockData';

export async function GET() {
  return NextResponse.json(mockSchedule);
}

export async function POST(request: Request) {
  const data = await request.json();
  const newItem = { id: Date.now().toString(), ...data };
  return NextResponse.json(newItem, { status: 201 });
}
