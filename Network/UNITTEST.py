

"""Network and miner models used to simulate distributed block creation and propagation."""


import unittest
import threading
from threading import Event
import os
from DAGVisulizer.dagVisulizer_Jmaxtip_DY import DAGVisualizer
from Network.GF_New_JMaztipMiner_DY_THR import Miner
from Network.Delaymatrix import MinerDelayMatrix
import unittest

class TestMinerMethods(unittest.TestCase):
    """Encapsulate related simulation state and behaviour for the TestMinerMethods component."""
    def setUp(self):
        """Setup used by the GhostForge research simulation."""
        self.delay_matrix = MinerDelayMatrix()
        self.visualizer = DAGVisualizer()
        self.miner = Miner('M1', self.delay_matrix, self.visualizer)
        self.miner.dag.add_node('A')
        self.miner.dag.add_node('B')
        self.miner.dag.add_node('C')
        self.miner.dag.add_node('D')
        self.miner.dag.add_edge('G', 'A')
        self.miner.dag.add_edge('A', 'B')
        self.miner.dag.add_edge('B', 'C')
        self.miner.dag.add_edge('C', 'D')
        self.miner.previous_order = ['G', 'A', 'B', 'C', 'D']

    def test_update_stability_count(self):
        """Test update stability count used by the GhostForge research simulation."""
        self.miner.order_history = [['G', 'A', 'B', 'C', 'D']]
        for _ in range(9):
            self.miner.update_stability_count()
        self.miner.update_stability_count()
        self.assertIn('D', self.miner.locked_blocks)

    def test_apply_protocol_with_locked_blocks(self):
        """Test apply protocol with locked blocks used by the GhostForge research simulation."""
        self.miner.locked_blocks = set(['G', 'A', 'B'])
        print("Before applying protocol with locked blocks")
        print(f"Locked blocks: {self.miner.locked_blocks}")
        print(f"Current order: {self.miner.previous_order}")
        self.miner.apply_protocol_with_locked_blocks()
        print("After applying protocol with locked blocks")
        print(f"New order: {self.miner.previous_order}")
        self.assertIn('C', self.miner.previous_order)
        self.assertNotIn('A', self.miner.previous_order)

if __name__ == '__main__':
    unittest.main()
