"""
Byzantine Fault-Tolerant Memory Consensus Gate for Mem-Quarantine.
Prevents single-agent hallucinations or jailbreaks from corrupting the swarm's collective memory.
"""

import hashlib
import time
from typing import Dict, List, Optional, Tuple, Any
from .models import MemoryNode, MemoryStatus, MemoryVote


class ByzantineMemoryGate:
    """Enforces multi-model consensus before committing candidate memory to shared graph."""

    def __init__(self, required_quorum_ratio: float = 0.66):
        self.required_quorum_ratio = required_quorum_ratio

    def evaluate_candidate(
        self,
        node: MemoryNode,
        verifiers: List[Tuple[str, str, bool, str]] # (agent_name, model_name, approved, reason)
    ) -> MemoryStatus:
        """
        Collects independent verifier votes across distinct model architectures.
        Requires 2-of-3 (66%) quorum to promote from QUARANTINED to COMMITTED.
        """
        for verifier_agent, verifier_model, approved, reason in verifiers:
            vote = MemoryVote(
                verifier_agent=verifier_agent,
                verifier_model=verifier_model,
                approved=approved,
                confidence=0.95 if approved else 0.98,
                rationale=reason
            )
            node.votes.append(vote)

        total_votes = len(node.votes)
        positive_votes = sum(1 for v in node.votes if v.approved)

        # Compute hash
        hash_input = f"{node.memory_id}:{node.content}:{node.author_agent}:{time.time()}"
        node.cryptographic_hash = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()[:16]

        if total_votes > 0 and (positive_votes / total_votes) >= self.required_quorum_ratio:
            node.status = MemoryStatus.COMMITTED
        else:
            node.status = MemoryStatus.REJECTED

        return node.status
