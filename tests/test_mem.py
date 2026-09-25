"""
Comprehensive Unit Test Suite for Mem-Quarantine.
"""

import unittest
from mem_quarantine.models import MemoryStatus
from mem_quarantine.consensus import ByzantineMemoryGate
from mem_quarantine.graph_firewall import MemoryGraphFirewall


class TestMemQuarantine(unittest.TestCase):

    def setUp(self):
        self.firewall = MemoryGraphFirewall()

    def test_byzantine_consensus_approval(self):
        """Test candidate memory promotes to COMMITTED when quorum is met."""
        node = self.firewall.stage_memory("Safe system config", "agent_1", "claude-opus-5-5")
        self.assertEqual(node.status, MemoryStatus.QUARANTINED)

        verifiers = [
            ("agent_2", "gpt-6-astra", True, "Fact verified"),
            ("agent_3", "gemini-3-8-flash-cyber", True, "Fact verified")
        ]
        status = self.firewall.verify_and_commit(node.memory_id, verifiers)
        self.assertEqual(status, MemoryStatus.COMMITTED)
        self.assertEqual(node.status, MemoryStatus.COMMITTED)
        self.assertTrue(len(node.cryptographic_hash) > 0)

    def test_byzantine_consensus_rejection(self):
        """Test hostile memory is rejected when quorum fails."""
        node = self.firewall.stage_memory("Hostile false fact", "agent_attacker", "gpt-6-sol")
        verifiers = [
            ("agent_2", "claude-opus-5-5", False, "Contradiction found"),
            ("agent_3", "gemini-3-8-flash-cyber", False, "Security violation")
        ]
        status = self.firewall.verify_and_commit(node.memory_id, verifiers)
        self.assertEqual(status, MemoryStatus.REJECTED)

    def test_tainted_lineage_cascading_excision(self):
        """Test that excising a parent memory cascades down to all derived child memories."""
        m_parent = self.firewall.stage_memory("Parent Fact", "agent_1", "claude-opus-5-5")
        self.firewall.verify_and_commit(m_parent.memory_id, [("v1", "gpt-6-astra", True, "ok")])

        m_child1 = self.firewall.stage_memory("Child 1 Fact", "agent_2", "gpt-6-astra", [m_parent.memory_id])
        self.firewall.verify_and_commit(m_child1.memory_id, [("v1", "gpt-6-astra", True, "ok")])

        m_grandchild = self.firewall.stage_memory("Grandchild Fact", "agent_3", "claude-opus-5-5", [m_child1.memory_id])
        self.firewall.verify_and_commit(m_grandchild.memory_id, [("v1", "gpt-6-astra", True, "ok")])

        self.assertEqual(len(self.firewall.get_active_canonical_memories()), 3)

        # Excise parent
        excised = self.firewall.excise_tainted_lineage(m_parent.memory_id)
        self.assertEqual(len(excised), 3)
        self.assertIn(m_parent.memory_id, excised)
        self.assertIn(m_child1.memory_id, excised)
        self.assertIn(m_grandchild.memory_id, excised)

        # Active canonical memories must now be 0
        self.assertEqual(len(self.firewall.get_active_canonical_memories()), 0)


if __name__ == "__main__":
    unittest.main()
