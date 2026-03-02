# 🧠 OpenClaw Dynamic Memory Architecture

## Philosophy: Cognitive-Inspired Tiered Memory

This system mirrors how the human brain manages information — sensory buffer → working memory → episodic/semantic long-term memory — combined with modern AI techniques like RAG, memory consolidation, and forgetting curves.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│ INCOMING MESSAGE                                    │
└──────────────────────┬──────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────┐
│ TIER 0: Sensory Buffer (In-context)                │
│ Last 3–5 exchanges · Raw, unprocessed · Ephemeral  │
└──────────────────────┬──────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────┐
│ TIER 1: Working Memory (Session State)             │
│ Current conversation goals · Active entities        │
│ Temporary preferences · Lasts 1 session             │
└──────────────────────┬──────────────────────────────┘
                       ▼
              ┌─────────────┴─────────────┐
              ▼                           ▼
┌───────────────┐             ┌──────────────────────┐
│ TIER 2:       │             │ TIER 3:              │
│ Episodic      │             │ Semantic             │
│ Memory        │             │ Memory               │
│ (Events)      │             │ (Facts/Knowledge)    │
│               │             │                      │
│ "User said X  │             │ "User prefers Y"     │
│ on Monday"    │             │ "User's name is Z"  │
└───────┬───────┘             └──────────┬───────────┘
        └─────────────┬─────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────┐
│ TIER 4: Archival Memory (Long-term)                │
│ Compressed summaries · User profile · Patterns     │
│ Persists indefinitely · Retrieved via similarity   │
└─────────────────────────────────────────────────────┘
```

---

## Memory Data Schemas

### Working Memory Entry

```json
{
  "session_id": "uuid",
  "created_at": "ISO8601",
  "active_topics": ["topic1", "topic2"],
  "active_entities": { "person": [], "project": [], "preference": [] },
  "current_goal": "string",
  "conversation_tone": "formal|casual|technical",
  "unresolved_threads": []
}
```

### Episodic Memory Entry

```json
{
  "id": "uuid",
  "timestamp": "ISO8601",
  "event_summary": "string (1-2 sentences)",
  "entities_involved": ["entity1"],
  "emotional_valence": "positive|neutral|negative",
  "importance_score": "0.0–1.0",
  "decay_rate": "0.0–1.0",
  "tags": ["tag1", "tag2"],
  "raw_content_hash": "sha256"
}
```

### Semantic Memory Entry

```json
{
  "id": "uuid",
  "fact": "string",
  "category": "preference|identity|relationship|skill|goal",
  "confidence": "0.0–1.0",
  "source_episodes": ["episode_id_1"],
  "last_confirmed": "ISO8601",
  "contradicts": ["other_fact_id"],
  "embedding": [0.123, ...]
}
```

### User Profile (Archival)

```json
{
  "user_id": "string",
  "name": "string",
  "communication_style": "string",
  "key_facts": {},
  "recurring_themes": [],
  "preferences": {},
  "last_summarized": "ISO8601",
  "session_count": 0,
  "total_interactions": 0
}
```

---

## Core Memory Algorithms

### 1. Memory Formation (Write)

```python
class MemoryManager:
    def process_message(self, message: str, role: str, context: dict):
        """Pipeline: Extract → Score → Store → Consolidate"""

        # Step 1: Entity & Intent Extraction (via LLM or NER)
        entities = self.extract_entities(message)
        intent = self.classify_intent(message)

        # Step 2: Importance Scoring (Ebbinghaus + novelty)
        importance = self.score_importance(message, entities, context)

        # Step 3: Route to appropriate memory tier
        if importance > 0.7:
            self.write_episodic(message, entities, importance)
            if self.contains_fact(message):
                self.upsert_semantic(entities, message)

        # Step 4: Update working memory
        self.update_working_memory(intent, entities)

        # Step 5: Trigger consolidation if threshold met
        if self.should_consolidate():
            self.consolidate_to_longterm()
```

### 2. Importance Scoring

```python
def score_importance(self, message: str, entities: list, context: dict) -> float:
    score = 0.0

    # Novelty: Is this new information?
    if not self.exists_in_memory(message):
        score += 0.3

    # Entity density: More entities = more important
    score += min(len(entities) * 0.1, 0.3)

    # Emotional markers (explicit or inferred)
    if self.has_emotional_content(message):
        score += 0.2

    # User explicitly asks to remember
    if any(kw in message.lower() for kw in ["remember", "don't forget", "important", "always"]):
        score += 0.4

    # Contradiction with existing facts (must update)
    if self.contradicts_existing(message):
        score += 0.35

    return min(score, 1.0)
```

### 3. Memory Recall (Read) — Hybrid RAG

```python
def recall(self, query: str, context: dict) -> dict:
    """Multi-strategy retrieval: recency + semantic similarity + graph traversal"""

    results = {
        "working": self.get_working_memory(),
        "episodic": [],
        "semantic": [],
        "profile": self.get_user_profile()
    }

    # Strategy 1: Semantic similarity search (vector DB)
    query_embedding = self.embed(query)
    semantic_hits = self.vector_search(query_embedding, top_k=5)

    # Strategy 2: Recency boost (recent memories more relevant)
    recency_hits = self.get_recent_episodes(n=3)

    # Strategy 3: Entity matching
    entities = self.extract_entities(query)
    entity_hits = self.search_by_entities(entities)

    # Strategy 4: Keyword/tag matching (fallback)
    keyword_hits = self.search_by_tags(query)

    # Merge & re-rank (RRF: Reciprocal Rank Fusion)
    all_hits = self.reciprocal_rank_fusion(
        [semantic_hits, recency_hits, entity_hits, keyword_hits]
    )

    results["episodic"] = all_hits[:5]
    results["semantic"] = self.get_relevant_facts(entities)

    return results
```

### 4. Memory Decay (Ebbinghaus Forgetting Curve)

```python
def apply_decay(self):
    """Run periodically — remove or downgrade stale memories"""

    now = datetime.utcnow()

    for memory in self.get_all_episodic():
        age_days = (now - memory.timestamp).days

        # R = e^(-t/S) — retention formula
        # t = time elapsed, S = stability (importance-based)
        stability = memory.importance_score * 30  # max 30 days for unreviewed
        retention = math.exp(-age_days / stability)

        if retention < 0.2:
            if memory.importance_score > 0.8:
                # Compress to semantic fact instead of deleting
                self.compress_to_semantic(memory)
            else:
                self.archive_or_delete(memory)
        else:
            memory.decay_rate = retention
            self.update(memory)
```

### 5. Memory Consolidation (Session End)

```python
def consolidate_to_longterm(self):
    """Compress episodic memories into semantic facts + update user profile"""

    recent_episodes = self.get_unconsolidated_episodes()
    if not recent_episodes:
        return

    # LLM-powered summarization
    summary_prompt = f"""
    Given these conversation episodes:
    {json.dumps([e.dict() for e in recent_episodes], indent=2)}

    Extract:
    1. Key facts about the user (name, preferences, goals, skills)
    2. Important events to remember
    3. A 2-sentence session summary
    4. Updated user communication style

    Return as JSON.
    """

    consolidated = self.llm_call(summary_prompt)

    # Update semantic memory (with contradiction detection)
    for fact in consolidated["facts"]:
        self.upsert_semantic_with_conflict_resolution(fact)

    # Update archival user profile
    self.update_user_profile(consolidated)

    # Mark episodes as consolidated
    self.mark_consolidated(recent_episodes)
```

---

## Memory Injection into Prompts

```python
def build_memory_context(self, query: str) -> str:
    """Construct the memory block injected into every system prompt"""

    recalled = self.recall(query)

    blocks = []

    # User profile (always include)
    profile = recalled["profile"]
    if profile:
        blocks.append(f"## User Profile\n{self._format_profile(profile)}")

    # Key facts
    facts = recalled["semantic"]
    if facts:
        facts_str = "\n".join(f"- {f['fact']}" for f in facts[:8])
        blocks.append(f"## Known Facts\n{facts_str}")

    # Recent relevant episodes
    episodes = recalled["episodic"]
    if episodes:
        ep_str = "\n".join(
            f"- [{e['timestamp'][:10]}] {e['event_summary']}"
            for e in episodes[:4]
        )
        blocks.append(f"## Relevant Memory\n{ep_str}")

    # Working memory (current session context)
    working = recalled["working"]
    if working.get("current_goal"):
        blocks.append(f"## Current Session Goal\n{working['current_goal']}")

    return "\n\n".join(blocks)
```

### System Prompt Template

```
<memory>
{memory_context}
</memory>

You are OpenClaw. Use the above memory to personalize your responses.
If the user asks you to remember something, confirm it.
If new information contradicts your memory, update your understanding.
```

---

## Storage Backend Recommendations

| Tier | Storage | Why |
|------|---------|-----|
| Working Memory | Redis (TTL: session) | Fast, ephemeral, sub-ms reads |
| Episodic Memory | PostgreSQL + pgvector | Structured + vector search |
| Semantic Memory | PostgreSQL + pgvector | Fact deduplication + similarity |
| Archival Profile | PostgreSQL (JSON column) | Durable, queryable |
| Embeddings | pgvector or Qdrant | High-performance ANN search |

---

## Advanced Techniques

### Contradiction Resolution

```python
def upsert_semantic_with_conflict_resolution(self, new_fact: dict):
    similar = self.find_similar_facts(new_fact["fact"], threshold=0.85)

    for existing in similar:
        if self.is_contradiction(existing, new_fact):
            if new_fact["confidence"] > existing["confidence"]:
                # New fact wins — update
                self.update_fact(existing["id"], new_fact)
                self.log_contradiction(existing, new_fact)
            else:
                # Keep old, lower new fact's confidence
                new_fact["confidence"] *= 0.7
                self.insert_fact(new_fact)
```

### Memory Reflection (Periodic)

```python
# Run every N sessions or N days
def reflect_on_memories(self):
    """LLM-driven introspection: find patterns, infer high-level beliefs"""

    all_facts = self.get_all_semantic_facts()
    all_summaries = self.get_session_summaries(last_n=10)

    reflection_prompt = f"""
    Analyze these facts and session summaries about the user.

    Identify:
    - Long-term goals and values
    - Behavioral patterns
    - Evolving preferences
    - Potential needs they haven't expressed but might have

    Return high-confidence meta-facts as JSON.
    """

    meta_facts = self.llm_call(reflection_prompt)

    for fact in meta_facts:
        fact["category"] = "inferred"
        fact["confidence"] *= 0.8  # Inferred = slightly lower confidence
        self.upsert_semantic_with_conflict_resolution(fact)
```

---

## OpenClaw Integration Pseudocode

```python
class OpenClawBot:
    def __init__(self):
        self.memory = MemoryManager(
            vector_db="pgvector",
            llm=ClaudeClient(),
            config={
                "max_working_memory_items": 20,
                "episodic_retention_days": 90,
                "consolidation_trigger": 15,  # episodes
                "decay_interval_hours": 24,
                "embedding_model": "text-embedding-3-small"
            }
        )

    async def chat(self, user_id: str, message: str) -> str:
        # 1. Load session context
        self.memory.load_session(user_id)

        # 2. Recall relevant memories
        memory_context = self.memory.build_memory_context(message)

        # 3. Build prompt with memory
        prompt = self.build_prompt(message, memory_context)

        # 4. Call LLM
        response = await self.llm.complete(prompt)

        # 5. Process new memories from this exchange
        self.memory.process_message(message, role="user")
        self.memory.process_message(response, role="assistant")

        # 6. Async: decay + consolidation (non-blocking)
        asyncio.create_task(self.memory.run_maintenance())

        return response
```

---

## Key Design Principles

1. **Primacy & Recency** — Always include earliest and most recent context
2. **Ebbinghaus Forgetting Curve** — Decay unimportant memories; strengthen recalled ones
3. **Spreading Activation** — Retrieving one memory activates related ones (entity graph)
4. **Consolidation** — Short-term → long-term via periodic LLM summarization
5. **Confidence Scoring** — Every fact has confidence; contradictions resolved by confidence + recency
6. **Graceful Degradation** — If memory store is unavailable, fall back to in-context only
7. **Privacy-first** — Hash/encrypt PII; give users ability to delete their memory

---

## Quick Start Checklist

- [ ] Set up PostgreSQL with `pgvector` extension
- [ ] Initialize Redis for working memory
- [ ] Implement `MemoryManager` class
- [ ] Add memory injection to your system prompt builder
- [ ] Set up cron job for decay + consolidation
- [ ] Add `remember: true` flag detection in messages
- [ ] Build memory dashboard for debugging (optional but recommended)
