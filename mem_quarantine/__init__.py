"""
Mem-Quarantine: Byzantine Fault-Tolerant Memory Firewall for Shared Agent Swarms.
Supports Claude Opus 5.5, GPT-6 Astra, and Gemini 3.8 Flash Cyber.
"""

from .models import (
    MemoryStatus,
    MemoryVote,
    MemoryNode,
    QuarantineAuditReport,
)
from .consensus import ByzantineMemoryGate
from .graph_firewall import MemoryGraphFirewall

__version__ = "1.0.0"
__all__ = [
    "MemoryStatus",
    "MemoryVote",
    "MemoryNode",
    "QuarantineAuditReport",
    "ByzantineMemoryGate",
    "MemoryGraphFirewall",
]
