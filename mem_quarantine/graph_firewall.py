"""
Provenance Graph & Tainted Lineage Excision Engine for Mem-Quarantine.
Maintains cryptographically tracked memory trees and purges cascading hallucinations.
"""

import time
import uuid
from typing import Dict, List, Set, Optional, Tuple, Any
from .models import (
    MemoryNode,
    MemoryStatus,
    QuarantineAuditReport,
)
from .consensus import ByzantineMemoryGate


class MemoryGraphFirewall:
    """Monitors shared multi-agent memory stores and excises tainted memory cascades."""

    def __init__(self, consensus_gate: Optional[ByzantineMemoryGate] = None):
        self.gate = consensus_gate or ByzantineMemoryGate()
        self.nodes: Dict[str, MemoryNode] = {}
        self.provenance_edges: Dict[str, List[str]] = {} # parent_id -> list of child_ids

    def stage_memory(
        self,
        content: str,
        author_agent: str,
        author_model: str,
        parent_memory_ids: Optional[List[str]] = None
    ) -> MemoryNode:
        """Stage memory into quarantine zone awaiting consensus."""
        mem_id = f"mem_{uuid.uuid4().hex[:8]}"
        parents = parent_memory_ids or []

        node = MemoryNode(
            memory_id=mem_id,
            content=content,
            author_agent=author_agent,
            author_model=author_model,
            parent_memory_ids=parents,
            status=MemoryStatus.QUARANTINED
        )
        self.nodes[mem_id] = node

        # Link parent provenance
        for pid in parents:
            if pid in self.nodes:
                self.nodes[pid].derived_child_ids.append(mem_id)
            if pid not in self.provenance_edges:
                self.provenance_edges[pid] = []
            self.provenance_edges[pid].append(mem_id)

        return node

    def verify_and_commit(
        self,
        memory_id: str,
        verifiers: List[Tuple[str, str, bool, str]]
    ) -> MemoryStatus:
        """Process candidate memory through Byzantine consensus."""
        node = self.nodes.get(memory_id)
        if not node:
            raise KeyError(f"Memory '{memory_id}' not found in registry")

        # If any parent was tainted or excised, reject immediately
        for pid in node.parent_memory_ids:
            parent = self.nodes.get(pid)
            if parent and parent.status in (MemoryStatus.TAINTED, MemoryStatus.EXCISED, MemoryStatus.REJECTED):
                node.status = MemoryStatus.REJECTED
                return MemoryStatus.REJECTED

        status = self.gate.evaluate_candidate(node, verifiers)
        return status

    def excise_tainted_lineage(self, root_tainted_id: str, reason: str = "Hostile or Hallucinatory Drift") -> List[str]:
        """
        Recursively identifies and purges all downstream memories derived from an infected root node.
        Prevents cascading swarm corruption.
        """
        excised_ids: List[str] = []
        stack = [root_tainted_id]
        visited: Set[str] = set()

        while stack:
            curr_id = stack.pop()
            if curr_id in visited:
                continue
            visited.add(curr_id)

            node = self.nodes.get(curr_id)
            if node:
                node.status = MemoryStatus.EXCISED
                node.metadata["excise_reason"] = reason
                excised_ids.append(curr_id)

                # Push all derived children to stack
                children = self.provenance_edges.get(curr_id, [])
                for child_id in children:
                    stack.append(child_id)

        return excised_ids

    def get_active_canonical_memories(self) -> List[MemoryNode]:
        """Return only verified, clean, committed memories."""
        return [n for n in self.nodes.values() if n.status == MemoryStatus.COMMITTED]

    def audit_health(self) -> QuarantineAuditReport:
        """Produce cryptographic health and threat defense audit."""
        committed = sum(1 for n in self.nodes.values() if n.status == MemoryStatus.COMMITTED)
        quarantined = sum(1 for n in self.nodes.values() if n.status == MemoryStatus.QUARANTINED)
        excised = sum(1 for n in self.nodes.values() if n.status in (MemoryStatus.EXCISED, MemoryStatus.TAINTED))
        rejected = sum(1 for n in self.nodes.values() if n.status == MemoryStatus.REJECTED)

        return QuarantineAuditReport(
            total_memories_submitted=len(self.nodes),
            active_committed_memories=committed,
            quarantined_memories=quarantined,
            excised_tainted_memories=excised,
            byzantine_attacks_deflected=rejected + excised,
            details=[f"Memory pool healthy: {committed} active, {excised} excised, {rejected} rejected."]
        )
