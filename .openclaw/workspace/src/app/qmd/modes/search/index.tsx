import React, { useState, useEffect } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Search, Activity, AlertCircle, History } from 'lucide-react';

interface ScoreBreakdown {
  semantic: number;
  fts: number;
}

interface SearchResult {
  id: string;
  title: string;
  snippet: string;
  score: number;
  breakdown: ScoreBreakdown;
  source: string;
}

interface ZeroResultQuery {
  query: string;
  timestamp: string;
}

export default function SearchMode() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [zeroResults, setZeroResults] = useState<ZeroResultQuery[]>([]);
  const [activityData, setActivityData] = useState<{date: string, count: number}[]>([]);

  const performSearch = async (searchQuery: string) => {
    if (!searchQuery) return;
    setLoading(true);
    try {
      const res = await fetch(`/api/qmd/search?q=${encodeURIComponent(searchQuery)}`);
      const data = await res.json();
      
      if (data.results && data.results.length === 0) {
        setZeroResults(prev => [{ query: searchQuery, timestamp: new Date().toISOString() }, ...prev].slice(0, 10));
      }
      setResults(data.results || []);
    } catch (e) {
      console.error('Search error:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Fetch search volume/activity
    fetch('/api/qmd/activity')
      .then(res => res.json())
      .then(data => setActivityData(data.timeline || []))
      .catch(() => setActivityData([
        { date: 'Mon', count: 12 }, { date: 'Tue', count: 19 }, { date: 'Wed', count: 15 },
        { date: 'Thu', count: 22 }, { date: 'Fri', count: 30 }, { date: 'Sat', count: 10 }, { date: 'Sun', count: 8 }
      ]));
  }, []);

  return (
    <div className="flex h-full w-full gap-6 p-6 overflow-hidden text-foreground bg-background">
      {/* Main Search Area */}
      <div className="flex-1 flex flex-col gap-6 h-full overflow-hidden">
        <div className="relative group">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
          <Input 
            className="pl-10 h-12 rounded-xl border-border bg-card backdrop-blur-xl transition-all focus:ring-2 ring-primary/20"
            placeholder="Search memory, documents, and patterns..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && performSearch(query)}
          />
          <Button 
            onClick={() => performSearch(query)} 
            className="absolute right-2 top-1/2 -translate-y-1/2 h-8 px-3 rounded-lg"
          >
            {loading ? '...' : 'Search'}
          </Button>
        </div>

        <div className="flex-1 overflow-y-auto space-y-4 pr-2">
          {results.length === 0 && !loading && (
            <div className="h-full flex flex-col items-center justify-center text-muted-foreground space-y-2 opacity-60">
              <Search className="w-12 h-12 stroke-1" />
              <p>Enter a query to begin the autopsy</p>
            </div>
          )}
          
          {results.map(result => (
            <div key={result.id} className="p-4 rounded-xl border border-border bg-card backdrop-blur-xl hover:border-primary/30 transition-all group">
              <div className="flex justify-between items-start mb-2">
                <h3 className="font-medium text-lg group-hover:text-primary transition-colors">{result.title}</h3>
                <Badge variant="outline" className="font-mono text-xs">
                  {result.source}
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground mb-4 line-clamp-2">{result.snippet}</p>
              
              {/* Score Autopsy */}
              <div className="space-y-2">
                <div className="flex justify-between text-[10px] uppercase tracking-wider font-bold text-muted-foreground">
                  <span>Score Breakdown</span>
                  <span>{(result.score * 100).toFixed(0)}% Match</span>
                </div>
                <div className="h-2 w-full bg-black/20 dark:bg-black/40 rounded-full overflow-hidden flex">
                  <div 
                    className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-500" 
                    style={{ width: `${result.breakdown.semantic * 100}%` }}
                    title="Semantic Score"
                  />
                  <div 
                    className="h-full bg-gradient-to-r from-emerald-500 to-amber-500 transition-all duration-500" 
                    style={{ width: `${result.breakdown.fts * 100}%` }}
                    title="FTS Score"
                  />
                </div>
                <div className="flex gap-4 text-[10px]">
                  <div className="flex items-center gap-1">
                    <div className="w-2 h-2 rounded-full bg-blue-500" />
                    <span>Semantic</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <div className="w-2 h-2 rounded-full bg-emerald-500" />
                    <span>FTS/Keyword</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Search Timeline (Bottom) */}
        <div className="p-4 rounded-xl border border-border bg-card backdrop-blur-xl flex items-center gap-4">
          <div className="p-2 rounded-lg bg-primary/10">
            <Activity className="w-4 h-4 text-primary" />
          </div>
          <div className="flex-1 flex items-end gap-1 h-8">
            {activityData.map((d, i) => (
              <div 
                key={i} 
                className="flex-1 bg-primary/20 rounded-t-sm hover:bg-primary/40 transition-colors relative group"
                style={{ height: `${(d.count / 30) * 100}%` }}
              >
                <span className="absolute -top-5 left-1/2 -translate-x-1/2 text-[8px] hidden group-hover:block bg-foreground text-background px-1 rounded">
                  {d.count}
                </span>
              </div>
            ))}
          </div>
          <span className="text-[10px] uppercase font-bold text-muted-foreground tracking-tighter">
            Volume (7d)
          </span>
        </div>
      </div>

      {/* Zero-Result Radar (Side Panel) */}
      <div className="w-72 flex flex-col gap-4 h-full">
        <div className="p-4 rounded-xl border border-border bg-card backdrop-blur-xl h-full flex flex-col">
          <div className="flex items-center gap-2 mb-4">
            <AlertCircle className="w-4 h-4 text-amber-500" />
            <h2 className="font-bold text-sm uppercase tracking-tight">Zero-Result Radar</h2>
          </div>
          
          <div className="flex-1 overflow-y-auto space-y-2">
            {zeroResults.length === 0 ? (
              <p className="text-xs text-muted-foreground italic opacity-50">No memory gaps detected yet.</p>
            ) : (
              zeroResults.map((item, i) => (
                <div key={i} className="p-2 rounded-lg bg-black/20 dark:bg-black/40 border border-border/50 hover:border-amber-500/50 transition-all cursor-pointer group">
                  <div className="text-xs font-medium truncate group-hover:text-amber-400 transition-colors">
                    {item.query}
                  </div>
                  <div className="text-[9px] text-muted-foreground mt-1 flex items-center gap-1">
                    <History className="w-2 h-2" />
                    {new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              ))
            )}
          </div>
          
          <div className="mt-4 pt-4 border-t border-border text-[10px] text-muted-foreground leading-relaxed">
            Queries here represent gaps in the Knowledge Model. Consider adding context to ai-memory to fill these voids.
          </div>
        </div>
      </div>
    </div>
  );
}
