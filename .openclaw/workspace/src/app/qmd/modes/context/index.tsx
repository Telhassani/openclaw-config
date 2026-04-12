"use client";

import React, { useState, useEffect } from 'react';
import { 
  Search, 
  Database, 
  History, 
  Settings2, 
  FileText, 
  Zap, 
  CheckCircle2, 
  Circle
} from 'lucide-react';
import { 
  Card, 
  CardContent, 
  CardHeader, 
  CardTitle, 
  CardDescription 
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  Tooltip, 
  TooltipContent, 
  TooltipProvider, 
  TooltipTrigger 
} from "@/components/ui/tooltip";

interface InjectionLog {
  id: string;
  timestamp: string;
  source: string;
  snippet: string;
  tokens: number;
}

interface Collection {
  id: string;
  name: string;
  enabled: boolean;
}

interface SimulationResult {
  source: string;
  snippet: string;
  score: number;
}

export default function ContextMode() {
  const [logs, setLogs] = useState<InjectionLog[]>([]);
  const [collections, setCollections] = useState<Collection[]>([]);
  const [simQuery, setSimQuery] = useState('');
  const [simResults, setSimResults] = useState<SimulationResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetchLogs();
    fetchCollections();
  }, []);

  async function fetchLogs() {
    try {
      const res = await fetch('/api/qmd/context?action=logs');
      const data = await res.json();
      setLogs(data);
    } catch (e) {
      console.error("Failed to fetch logs", e);
    }
  }

  async function fetchCollections() {
    try {
      const res = await fetch('/api/qmd/context?action=collections');
      const data = await res.json();
      setCollections(data);
    } catch (e) {
      console.error("Failed to fetch collections", e);
    }
  }

  async function toggleCollection(id: string, enabled: boolean) {
    try {
      await fetch('/api/qmd/context', {
        method: 'POST',
        body: JSON.stringify({ action: 'toggle-collection', collectionId: id, enabled }),
      });
      setCollections(prev => prev.map(c => c.id === id ? { ...c, enabled } : c));
    } catch (e) {
      console.error("Failed to toggle collection", e);
    }
  }

  async function runSimulation() {
    if (!simQuery) return;
    setIsLoading(true);
    try {
      const res = await fetch('/api/qmd/context', {
        method: 'POST',
        body: JSON.stringify({ action: 'simulate', query: simQuery }),
      });
      const data = await res.json();
      setSimResults(data.results);
    } catch (e) {
      console.error("Simulation failed", e);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto animate-in fade-in duration-500">
      <header className="flex flex-col gap-2">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-purple-500/20 text-purple-400">
            <Zap size={24} />
          </div>
          <h1 className="text-3xl font-bold tracking-tight">Context Observatory</h1>
        </div>
        <p className="text-muted-foreground">
          Monitor, simulate, and tune the LLM's knowledge injection pipeline.
        </p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Scope Toggles */}
        <Card className="rounded-xl border border-border bg-card backdrop-blur-xl col-span-1">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Database size={18} className="text-purple-400" />
              Knowledge Scope
            </CardTitle>
            <CardDescription>Enable or disable indexed collections</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {collections.map(col => (
              <div key={col.id} className="flex items-center justify-between p-3 rounded-lg bg-black/20 dark:bg-black/40 border border-border/50 transition-colors hover:border-purple-500/30">
                <span className="text-sm font-medium">{col.name}</span>
                <Switch 
                  checked={col.enabled} 
                  onCheckedChange={(val) => toggleCollection(col.id, val)} 
                />
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Context Simulator */}
        <Card className="rounded-xl border border-border bg-card backdrop-blur-xl col-span-1 lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Search size={18} className="text-purple-400" />
              Context Simulator
            </CardTitle>
            <CardDescription>Predict what chunks will be retrieved for a specific query</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-2">
              <Input 
                placeholder="Ask a hypothetical question..." 
                value={simQuery}
                onChange={(e) => setSimQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && runSimulation()}
                className="bg-black/20 dark:bg-black/40"
              />
              <Button 
                onClick={runSimulation} 
                disabled={isLoading}
                className="bg-purple-600 hover:bg-purple-500 text-white"
              >
                {isLoading ? "Simulating..." : "Simulate"}
              </Button>
            </div>

            <div className="min-h-[200px] rounded-lg border border-border bg-black/10 dark:bg-black/20 p-4">
              {simResults.length === 0 ? (
                <div className="h-full flex items-center justify-center text-muted-foreground text-sm italic">
                  Enter a query to see retrieved context...
                </div>
              ) : (
                <div className="space-y-3">
                  {simResults.map((res, i) => (
                    <div key={i} className="p-3 rounded-lg border border-purple-500/20 bg-purple-500/5 space-y-2">
                      <div className="flex justify-between items-center">
                        <div className="flex items-center gap-2 text-xs font-mono text-purple-400">
                          <FileText size={12} />
                          {res.source}
                        </div>
                        <Badge variant="secondary" className="text-[10px] bg-purple-500/20 text-purple-300 border-none">
                          Score: {res.score}
                        </Badge>
                      </div>
                      <p className="text-sm text-foreground/80 line-clamp-3 italic">
                        "{res.snippet}"
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Injection Log */}
        <Card className="rounded-xl border border-border bg-card backdrop-blur-xl col-span-1 lg:col-span-3">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle className="text-lg flex items-center gap-2">
                <History size={18} className="text-purple-400" />
                Injection Log
              </CardTitle>
              <CardDescription>Last context injections sent to the LLM</CardDescription>
            </div>
            <Button variant="ghost" size="sm" onClick={fetchLogs} className="text-xs">
              Refresh
            </Button>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[400px] pr-4">
              <div className="space-y-3">
                {logs.length === 0 ? (
                  <div className="text-center py-10 text-muted-foreground italic">
                    No injection logs found.
                  </div>
                ) : (
                  logs.map((log) => (
                    <div 
                      key={log.id} 
                      className="group relative p-4 rounded-xl border border-border bg-gradient-to-r from-black/20 via-black/20 to-purple-500/10 dark:from-black/40 dark:via-black/40 dark:to-purple-900/20 transition-all hover:border-purple-500/40"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <div className="p-1 rounded-md bg-purple-500/20 text-purple-400">
                            <FileText size={14} />
                          </div>
                          <span className="text-xs font-mono font-medium text-foreground/70">{log.source}</span>
                        </div>
                        <div className="flex items-center gap-3">
                          <Badge variant="outline" className="text-[10px] font-mono opacity-60">
                            {log.tokens} tokens
                          </Badge>
                          <span className="text-[10px] text-muted-foreground">
                            {new Date(log.timestamp).toLocaleTimeString()}
                          </span>
                        </div>
                      </div>
                      <div className="pl-7 relative">
                        <div className="absolute left-0 top-0 bottom-0 w-px bg-purple-500/30" />
                        <p className="text-sm text-foreground/80 font-serif leading-relaxed italic">
                          {log.snippet}
                        </p>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
