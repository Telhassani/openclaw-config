import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const q = searchParams.get('q');

  if (!q) {
    return NextResponse.json({ results: [] }, { status: 400 });
  }

  // Mocking high-fidelity search results with score breakdowns
  // In a real implementation, this would call a vector database (e.g., Supabase pgvector)
  // and a full-text search index.
  const mockResults = [
    {
      id: '1',
      title: 'Memory Architecture Overview',
      snippet: 'The system utilizes a tiered memory approach with ai-memory as primary...',
      score: 0.92,
      breakdown: {
        semantic: 0.7,
        fts: 0.22,
      },
      source: 'docs/arch.md',
    },
    {
      id: '2',
      title: 'Session Management',
      snippet: 'Each session wakes up fresh, relying on ai-memory for persistence...',
      score: 0.85,
      breakdown: {
        semantic: 0.4,
        fts: 0.45,
      },
      source: 'docs/sessions.md',
    },
    {
      id: '3',
      title: 'Tooling Interface',
      snippet: 'The OpenClaw CLI provides a structured way to interact with host tools...',
      score: 0.61,
      breakdown: {
        semantic: 0.2,
        fts: 0.41,
      },
      source: 'docs/tools.md',
    },
  ];

  // Simulate zero-result case for specific query
  if (q.toLowerCase().includes('unknown-topic')) {
    return NextResponse.json({ results: [] });
  }

  return NextResponse.json({
    results: mockResults.filter(r => r.title.toLowerCase().includes(q.toLowerCase()) || r.snippet.toLowerCase().includes(q.toLowerCase())),
    query: q,
    timestamp: new Date().toISOString(),
  });
}
