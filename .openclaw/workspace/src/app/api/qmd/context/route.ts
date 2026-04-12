import { NextResponse } from 'next/server';

// Mock data for demonstration. In a real app, these would come from a database or log file.
const MOCK_INJECTIONS = [
  {
    id: '1',
    timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
    source: 'docs/architecture.md',
    snippet: 'The system uses a distributed event-bus for communication between microservices...',
    tokens: 120,
  },
  {
    id: '2',
    timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
    source: 'memory/2026-04-10.md',
    snippet: 'User prefers concise summaries and dark-mode UI components...',
    tokens: 85,
  },
  {
    id: '3',
    timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    source: 'src/app/api/qmd/route.ts',
    snippet: 'export async function GET() { return NextResponse.json({ status: "ok" }); }',
    tokens: 45,
  },
];

const MOCK_COLLECTIONS = [
  { id: 'docs', name: 'Project Documentation', enabled: true },
  { id: 'memory', name: 'Personal Memory', enabled: true },
  { id: 'code', name: 'Source Code', enabled: true },
  { id: 'web', name: 'Web Index', enabled: false },
];

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const action = searchParams.get('action');

  if (action === 'logs') {
    return NextResponse.json(MOCK_INJECTIONS);
  }

  if (action === 'collections') {
    return NextResponse.json(MOCK_COLLECTIONS);
  }

  return NextResponse.json({ error: 'Invalid action' }, { status: 400 });
}

export async function POST(request: Request) {
  const body = await request.json();
  const { action, query } = body;

  if (action === 'simulate') {
    // Mock simulation of RAG retrieval
    return NextResponse.json({
      results: [
        {
          source: 'docs/api-spec.md',
          snippet: `Found match for "${query}": The API provides endpoints for context management...`,
          score: 0.92,
        },
        {
          source: 'memory/recent.md',
          snippet: `Related context for "${query}": Previously discussed the implementation of the QMD dashboard.`,
          score: 0.78,
        },
      ],
    });
  }

  if (action === 'toggle-collection') {
    const { collectionId, enabled } = body;
    // In a real app, update database here
    return NextResponse.json({ status: 'ok', collectionId, enabled });
  }

  return NextResponse.json({ error: 'Invalid action' }, { status: 400 });
}
