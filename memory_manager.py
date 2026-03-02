#!/usr/bin/env python3
"""
OpenClaw Memory Manager
Tiered memory system: Working (Redis) → Episodic (PostgreSQL) → Semantic (PostgreSQL+Vector) → Archival (Profile)
"""

import os
import json
import hashlib
import re
import math
import uuid
import redis
import psycopg2
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6380))
PG_HOST = os.getenv('PG_HOST', 'localhost')
PG_PORT = int(os.getenv('PG_PORT', 5432))
PG_DB = os.getenv('PG_DB', 'memory')
PG_USER = os.getenv('PG_USER', os.getenv('USER', 'node'))
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

EMBEDDING_DIM = 1536  # OpenAI ada-002


class MemoryConfig:
    """Memory system configuration"""
    max_working_memory_items = 20
    episodic_retention_days = 90
    consolidation_trigger = 15  # episodes
    decay_interval_hours = 24
    embedding_model = "text-embedding-3-small"


@dataclass
class WorkingMemory:
    session_id: str
    user_id: str
    created_at: str
    active_topics: List[str]
    active_entities: Dict[str, List[str]]
    current_goal: str
    conversation_tone: str
    unresolved_threads: List[str]


@dataclass
class EpisodicMemory:
    id: str
    timestamp: str
    event_summary: str
    entities_involved: List[str]
    emotional_valence: str
    importance_score: float
    decay_rate: float
    tags: List[str]
    consolidated: bool
    session_id: str


@dataclass
class SemanticMemory:
    id: str
    fact: str
    category: str
    confidence: float
    source_episodes: List[str]
    last_confirmed: str
    embedding: List[float]


class MemoryManager:
    """
    Tiered memory system inspired by human cognition.
    """
    
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.session_id = str(uuid.uuid4())
        self._connect_redis()
        self._connect_pg()
        
    def _connect_redis(self):
        """Connect to Redis for working memory"""
        try:
            self.redis = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
            self.redis.ping()
            logger.info(f"Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Working memory will be in-memory only.")
            self.redis = None
            self._working_memory = {}  # Fallback to in-memory
            
    def _connect_pg(self):
        """Connect to PostgreSQL for episodic/semantic memory"""
        try:
            self.pg_conn = psycopg2.connect(
                host=PG_HOST, port=PG_PORT, database=PG_DB,
                user=PG_USER, password=os.getenv('PGPASSWORD', '')
            )
            self.pg_conn.autocommit = True
            self.pg_cursor = self.pg_conn.cursor()
            logger.info(f"Connected to PostgreSQL at {PG_HOST}:{PG_PORT}/{PG_DB}")
        except Exception as e:
            logger.error(f"PostgreSQL connection failed: {e}")
            self.pg_conn = None
            self.pg_cursor = None
    
    # ==================== WORKING MEMORY (Tier 1) ====================
    
    def load_working_memory(self, session_id: Optional[str] = None) -> WorkingMemory:
        """Load working memory from Redis for current session"""
        key = f"working:{self.user_id}:{session_id or self.session_id}"
        
        if self.redis:
            data = self.redis.hgetall(key)
            if data:
                return WorkingMemory(
                    session_id=data.get('session_id', ''),
                    user_id=data.get('user_id', ''),
                    created_at=data.get('created_at', ''),
                    active_topics=json.loads(data.get('active_topics', '[]')),
                    active_entities=json.loads(data.get('active_entities', '{}')),
                    current_goal=data.get('current_goal', ''),
                    conversation_tone=data.get('conversation_tone', 'neutral'),
                    unresolved_threads=json.loads(data.get('unresolved_threads', '[]'))
                )
        
        # Default working memory
        return WorkingMemory(
            session_id=self.session_id,
            user_id=self.user_id,
            created_at=datetime.utcnow().isoformat(),
            active_topics=[],
            active_entities={'person': [], 'project': [], 'preference': []},
            current_goal='',
            conversation_tone='neutral',
            unresolved_threads=[]
        )
    
    def save_working_memory(self, wm: WorkingMemory):
        """Save working memory to Redis"""
        key = f"working:{wm.user_id}:{wm.session_id}"
        data = {
            'session_id': wm.session_id,
            'user_id': wm.user_id,
            'created_at': wm.created_at,
            'active_topics': json.dumps(wm.active_topics),
            'active_entities': json.dumps(wm.active_entities),
            'current_goal': wm.current_goal,
            'conversation_tone': wm.conversation_tone,
            'unresolved_threads': json.dumps(wm.unresolved_threads)
        }
        
        if self.redis:
            self.redis.hset(key, mapping=data)
            self.redis.expire(key, 3600)  # 1 hour TTL
        else:
            self._working_memory[key] = data
    
    def update_working_memory(self, intent: str, entities: List[str]):
        """Update working memory with new intent and entities"""
        wm = self.load_working_memory()
        
        # Add intent as active topic
        if intent and intent not in wm.active_topics:
            wm.active_topics.append(intent)
            wm.active_topics = wm.active_topics[-MemoryConfig.max_working_memory_items:]
        
        # Add entities to appropriate category
        for entity in entities:
            entity_lower = entity.lower()
            if any(p in entity_lower for p in ['project', 'code', 'api', 'build']):
                if entity not in wm.active_entities['project']:
                    wm.active_entities['project'].append(entity)
            elif any(p in entity_lower for p in ['user', 'person', 'tariq']):
                if entity not in wm.active_entities['person']:
                    wm.active_entities['person'].append(entity)
            else:
                if entity not in wm.active_entities['preference']:
                    wm.active_entities['preference'].append(entity)
        
        self.save_working_memory(wm)
    
    # ==================== IMPORTANCE SCORING ====================
    
    def score_importance(self, message: str, entities: List[str], context: Dict = None) -> float:
        """
        Score importance of a message using Ebbinghaus forgetting curve principles.
        Returns score 0.0-1.0
        """
        score = 0.0
        message_lower = message.lower()
        
        # 1. Novelty: Is this new information?
        if not self._exists_in_memory(message):
            score += 0.3
        
        # 2. Entity density: More entities = more important
        score += min(len(entities) * 0.1, 0.3)
        
        # 3. Emotional markers
        emotional_markers = ['!', '??', 'urgent', 'asap', 'critical', 'important', 'please remember', 'never forget']
        if any(marker in message_lower for marker in emotional_markers):
            score += 0.2
        
        # 4. Explicit memory requests
        explicit_markers = ['remember', "don't forget", 'important', 'always', 'never']
        if any(marker in message_lower for marker in explicit_markers):
            score += 0.4
        
        # 5. Contradiction detection (would need semantic search - simplified here)
        # In full implementation, check against existing semantic memory
        
        return min(score, 1.0)
    
    def _exists_in_memory(self, message: str) -> bool:
        """Check if similar content exists in memory"""
        # Simple hash check - in production would use semantic similarity
        msg_hash = hashlib.sha256(message.encode()).hexdigest()[:16]
        key = f"hash:{self.user_id}:{msg_hash}"
        
        if self.redis:
            return bool(self.redis.exists(key))
        return False
    
    # ==================== EPISODIC MEMORY (Tier 2) ====================
    
    def write_episodic(self, message: str, entities: List[str], importance: float, 
                       emotional_valence: str = 'neutral', tags: List[str] = None):
        """Write to episodic memory (events)"""
        if not self.pg_cursor:
            logger.warning("No PostgreSQL connection, skipping episodic write")
            return
        
        # Generate summary (1-2 sentences)
        summary = self._generate_summary(message)
        
        # Hash for deduplication
        msg_hash = hashlib.sha256(message.encode()).hexdigest()
        
        query = """
            INSERT INTO episodic_memory 
            (event_summary, entities_involved, emotional_valence, importance_score, 
             tags, raw_content_hash, session_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        self.pg_cursor.execute(query, (
            summary, entities, emotional_valence, importance,
            tags or [], msg_hash, self.session_id
        ))
        
        # Track hash for novelty detection
        if self.redis:
            self.redis.setex(f"hash:{self.user_id}:{msg_hash[:16]}", 86400 * 30, "1")
        
        logger.info(f"Wrote episodic memory: {summary[:50]}...")
    
    def get_recent_episodes(self, n: int = 5) -> List[EpisodicMemory]:
        """Get recent episodic memories"""
        if not self.pg_cursor:
            return []
        
        query = """
            SELECT id, timestamp, event_summary, entities_involved, emotional_valence,
                   importance_score, decay_rate, tags, consolidated, session_id
            FROM episodic_memory
            WHERE user_id = %s OR user_id IS NULL
            ORDER BY timestamp DESC
            LIMIT %s
        """
        
        self.pg_cursor.execute(query, (self.user_id, n))
        rows = self.pg_cursor.fetchall()
        
        return [EpisodicMemory(
            id=str(r[0]), timestamp=r[1].isoformat() if r[1] else '',
            event_summary=r[2], entities_involved=r[3] or [],
            emotional_valence=r[4], importance_score=r[5] or 0.0,
            decay_rate=r[6] or 1.0, tags=r[7] or [], consolidated=r[8],
            session_id=r[9] or ''
        ) for r in rows]
    
    # ==================== SEMANTIC MEMORY (Tier 3) ====================
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using OpenAI"""
        if not OPENAI_API_KEY:
            # Return dummy embedding for testing
            import random
            return [random.random() for _ in range(EMBEDDING_DIM)]
        
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    
    def upsert_semantic(self, fact: str, category: str, confidence: float = 0.5):
        """Insert or update semantic memory (fact)"""
        if not self.pg_cursor:
            return
        
        embedding = self._get_embedding(fact)
        
        query = """
            INSERT INTO semantic_memory 
            (fact, category, confidence, source_episodes, last_confirmed, embedding)
            VALUES (%s, %s, %s, %s, NOW(), %s)
            ON CONFLICT DO NOTHING
        """
        
        self.pg_cursor.execute(query, (
            fact, category, confidence, [], json.dumps(embedding)
        ))
        
        logger.info(f"Wrote semantic memory: {fact[:50]}...")
    
    def search_semantic(self, query: str, top_k: int = 5) -> List[SemanticMemory]:
        """Search semantic memory by similarity"""
        if not self.pg_cursor:
            return []
        
        query_embedding = self._get_embedding(query)
        
        sql = """
            SELECT id, fact, category, confidence, source_episodes, last_confirmed
            FROM semantic_memory
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """
        
        self.pg_cursor.execute(sql, (json.dumps(query_embedding), top_k))
        rows = self.pg_cursor.fetchall()
        
        return [SemanticMemory(
            id=str(r[0]), fact=r[1], category=r[2], confidence=r[3] or 0.0,
            source_episodes=r[4] or [], last_confirmed=r[5].isoformat() if r[5] else '',
            embedding=[]
        ) for r in rows]
    
    def get_relevant_facts(self, entities: List[str]) -> List[SemanticMemory]:
        """Get facts related to specific entities"""
        if not self.pg_cursor or not entities:
            return []
        
        # Simple keyword search for now
        facts = []
        for entity in entities:
            self.pg_cursor.execute("""
                SELECT id, fact, category, confidence, source_episodes, last_confirmed
                FROM semantic_memory
                WHERE fact ILIKE %s
                LIMIT 3
            """, (f'%{entity}%',))
            
            for r in self.pg_cursor.fetchall():
                facts.append(SemanticMemory(
                    id=str(r[0]), fact=r[1], category=r[2], confidence=r[3] or 0.0,
                    source_episodes=r[4] or [], last_confirmed=r[5].isoformat() if r[5] else '',
                    embedding=[]
                ))
        
        return facts
    
    # ==================== USER PROFILE (Tier 4) ====================
    
    def get_user_profile(self) -> Dict[str, Any]:
        """Get user profile from archival memory"""
        if not self.pg_cursor:
            return {}
        
        self.pg_cursor.execute("""
            SELECT user_id, name, communication_style, key_facts, 
                   recurring_themes, preferences, session_count, total_interactions
            FROM user_profile
            WHERE user_id = %s
        """, (self.user_id,))
        
        row = self.pg_cursor.fetchone()
        if row:
            return {
                'user_id': row[0],
                'name': row[1],
                'communication_style': row[2],
                'key_facts': row[3] or {},
                'recurring_themes': row[4] or [],
                'preferences': row[5] or {},
                'session_count': row[6] or 0,
                'total_interactions': row[7] or 0
            }
        return {}
    
    def update_user_profile(self, updates: Dict[str, Any]):
        """Update user profile"""
        if not self.pg_cursor:
            return
        
        query = """
            INSERT INTO user_profile (user_id, name, communication_style, key_facts, 
                                       recurring_themes, preferences, session_count, total_interactions)
            VALUES (%s, %s, %s, %s, %s, %s, 1, 1)
            ON CONFLICT (user_id) DO UPDATE SET
                name = COALESCE(EXCLUDED.name, user_profile.name),
                communication_style = COALESCE(EXCLUDED.communication_style, user_profile.communication_style),
                key_facts = user_profile.key_facts || EXCLUDED.key_facts,
                recurring_themes = array(SELECT DISTINCT unnest(user_profile.recurring_themes || EXCLUDED.recurring_themes)),
                preferences = user_profile.preferences || EXCLUDED.preferences,
                session_count = user_profile.session_count + 1,
                total_interactions = user_profile.total_interactions + 1,
                last_summarized = NOW()
        """
        
        self.pg_cursor.execute(query, (
            self.user_id,
            updates.get('name'),
            updates.get('communication_style'),
            json.dumps(updates.get('key_facts', {})),
            updates.get('recurring_themes', []),
            json.dumps(updates.get('preferences', {}))
        ))
    
    # ==================== RECALL (Hybrid RAG) ====================
    
    def recall(self, query: str) -> Dict[str, Any]:
        """
        Multi-strategy retrieval: recency + semantic similarity + entity matching
        Returns dict with working, episodic, semantic, and profile memories
        """
        results = {
            'working': self.load_working_memory().__dict__,
            'episodic': [],
            'semantic': [],
            'profile': self.get_user_profile()
        }
        
        # Extract entities from query
        entities = self._extract_entities(query)
        
        # Strategy 1: Semantic similarity search
        semantic_hits = self.search_semantic(query, top_k=5)
        results['semantic'] = [asdict(s) for s in semantic_hits]
        
        # Strategy 2: Recency (recent memories)
        recent_episodes = self.get_recent_episodes(n=3)
        results['episodic'] = [asdict(e) for e in recent_episodes]
        
        # Strategy 3: Entity matching
        entity_facts = self.get_relevant_facts(entities)
        if entity_facts:
            results['semantic'].extend([asdict(f) for f in entity_facts])
        
        return results
    
    # ==================== MEMORY INJECTION ====================
    
    def build_memory_context(self, query: str) -> str:
        """Build memory context block for prompt injection"""
        recalled = self.recall(query)
        blocks = []
        
        # User profile
        profile = recalled['profile']
        if profile:
            blocks.append(f"## User Profile\nName: {profile.get('name', 'User')}\n"
                         f"Communication: {profile.get('communication_style', 'neutral')}")
        
        # Key facts
        facts = recalled.get('semantic', [])
        if facts:
            facts_str = "\n".join(f"- {f['fact']}" for f in facts[:8])
            blocks.append(f"## Known Facts\n{facts_str}")
        
        # Recent relevant episodes
        episodes = recalled.get('episodic', [])
        if episodes:
            ep_str = "\n".join(
                f"- [{e['timestamp'][:10] if e.get('timestamp') else 'recent'}] {e['event_summary']}"
                for e in episodes[:4]
            )
            blocks.append(f"## Recent Memory\n{ep_str}")
        
        # Working memory (current session)
        working = recalled.get('working', {})
        if working.get('current_goal'):
            blocks.append(f"## Current Session Goal\n{working['current_goal']}")
        
        return "\n\n".join(blocks)
    
    # ==================== HELPER METHODS ====================
    
    def _extract_entities(self, text: str) -> List[str]:
        """Simple entity extraction (placeholder - use NER in production)"""
        # Simple pattern matching
        patterns = [
            r'\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\b',  # Capitalized words
            r'@\w+',  # @mentions
        ]
        
        entities = []
        for pattern in patterns:
            entities.extend(re.findall(pattern, text))
        
        return list(set(entities))[:10]
    
    def _generate_summary(self, message: str) -> str:
        """Generate 1-2 sentence summary"""
        # Simple truncation for now - in production use LLM
        if len(message) <= 150:
            return message
        return message[:147] + "..."
    
    def contains_fact(self, message: str) -> bool:
        """Check if message contains a fact (simple heuristic)"""
        fact_markers = ['is', 'are', 'was', 'were', 'prefers', 'likes', 'hates', 'knows']
        return any(marker in message.lower() for marker in fact_markers)
    
    # ==================== MAINTAINENCE ====================
    
    def apply_decay(self):
        """Apply Ebbinghaus forgetting curve decay"""
        if not self.pg_cursor:
            return
        
        # Update decay rates based on age
        # R = e^(-t/S) where t is time in days, S is stability
        query = """
            UPDATE episodic_memory
            SET decay_rate = EXP(-EXTRACT(EPOCH FROM (NOW() - timestamp)) / 86400.0 / (COALESCE(importance_score, 0.5) * 30.0 + 1.0))
            WHERE importance_score > 0
        """
        self.pg_cursor.execute(query)
        
        # Archive or compress low-retention memories
        query = """
            SELECT id, event_summary, importance_score
            FROM episodic_memory
            WHERE decay_rate < 0.2 AND consolidated = FALSE
        """
        self.pg_cursor.execute(query)
        low_retention = self.pg_cursor.fetchall()
        
        for row in low_retention:
            if row[2] > 0.8:
                # Compress to semantic fact instead of deleting
                self.upsert_semantic(row[1], 'inferred', row[2] * 0.5)
            else:
                # Delete
                self.pg_cursor.execute("DELETE FROM episodic_memory WHERE id = %s", (row[0],))
        
        logger.info(f"Applied decay to episodic memories. Processed {len(low_retention)} memories.")
    
    def consolidate_to_longterm(self):
        """Consolidate episodic memories into semantic facts (session end)"""
        if not self.pg_cursor:
            return
        
        # Get unconsolidated episodes
        self.pg_cursor.execute("""
            SELECT id, event_summary, entities_involved, importance_score
            FROM episodic_memory
            WHERE consolidated = FALSE
            ORDER BY timestamp DESC
            LIMIT %s
        """, (MemoryConfig.consolidation_trigger,))
        
        episodes = self.pg_cursor.fetchall()
        
        if len(episodes) < MemoryConfig.consolidation_trigger:
            return
        
        # In production: Use LLM to extract facts and update profile
        # For now: simple extraction
        for ep in episodes:
            if self.contains_fact(ep[1]):
                self.upsert_semantic(ep[1], 'inferred', ep[3] * 0.7)
        
        # Mark as consolidated
        episode_ids = [str(ep[0]) for ep in episodes]
        self.pg_cursor.execute("""
            UPDATE episodic_memory
            SET consolidated = TRUE
            WHERE id = ANY(%s)
        """, (episode_ids,))
        
        logger.info(f"Consolidated {len(episodes)} episodic memories to semantic.")


# ==================== STANDALONE FUNCTIONS ====================

def process_message(user_id: str, message: str, role: str = 'user') -> Dict[str, Any]:
    """
    Process a message through the memory pipeline.
    Call this for each user message and assistant response.
    """
    memory = MemoryManager(user_id=user_id)
    
    # Extract entities
    entities = memory._extract_entities(message)
    
    # Score importance
    importance = memory.score_importance(message, entities)
    
    # Route to memory tiers
    if importance > 0.5:
        memory.write_episodic(message, entities, importance)
        
        if memory.contains_fact(message):
            memory.upsert_semantic(message, 'extracted', importance)
    
    # Update working memory
    intent = memory._extract_entities(message)[0] if entities else 'general'
    memory.update_working_memory(intent, entities)
    
    return {
        'session_id': memory.session_id,
        'importance': importance,
        'entities': entities
    }


def recall(user_id: str, query: str) -> str:
    """Get memory context for a query"""
    memory = MemoryManager(user_id=user_id)
    return memory.build_memory_context(query)


# ==================== CLI ====================

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='OpenClaw Memory Manager')
    parser.add_argument('action', choices=['process', 'recall', 'decay', 'consolidate'])
    parser.add_argument('--user', default='default')
    parser.add_argument('--message', '-m')
    parser.add_argument('--query', '-q')
    
    args = parser.parse_args()
    
    if args.action == 'process':
        result = process_message(args.user, args.message or '')
        print(json.dumps(result, indent=2))
    elif args.action == 'recall':
        context = recall(args.user, args.query or '')
        print(context)
    elif args.action == 'decay':
        memory = MemoryManager(user_id=args.user)
        memory.apply_decay()
        print("Decay applied")
    elif args.action == 'consolidate':
        memory = MemoryManager(user_id=args.user)
        memory.consolidate_to_longterm()
        print("Consolidation complete")
