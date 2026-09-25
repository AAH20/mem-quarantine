"""
Data models and provenance schemas for Mem-Quarantine.
Byzantine Fault-Tolerant Memory Firewall for Shared Agent Swarms.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Any
import time


class MemoryStatus(str, Enum):
    QUARANTINED = "QUARANTINED"     # Staged in sandbox, awaiting consensus verification
    COMMITTED = "COMMITTED"         # Formally accepted into shared canonical memory graph
    TAINTED = "TAINTED"             # Derived from compromised/hallucinating parent
    EXCISED = "EXCISED"             # Cryptographically pruned and neutralized
    REJECTED = "REJECTED"           # Failed initial Byzantine verification gate


@dataclass
class MemoryVote:
    verifier_agent: str
    verifier_model: str             # e.g. "claude-opus-5-5", "gemini-3-8-flash-cyber"
    approved: bool
    confidence: float
    rationale: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class MemoryNode:
    memory_id: str
    content: str
    author_agent: str
    author_model: str               # e.g. "gpt-6-astra", "claude-opus-5-5"
    timestamp: float = field(default_factory=time.time)
    parent_memory_ids: List[str] = field(default_factory=list)
    derived_child_ids: List[str] = field(default_factory=list)
    status: MemoryStatus = MemoryStatus.QUARANTINED
    votes: List[MemoryVote] = field(default_factory=list)
    cryptographic_hash: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QuarantineAuditReport:
    total_memories_submitted: int
    active_committed_memories: int
    quarantined_memories: int
    excised_tainted_memories: int
    byzantine_attacks_deflected: int
    duration_ms: float = 0.0
    details: List[str] = field(default_factory=list)
