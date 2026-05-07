"""Network and miner models used to simulate distributed block creation and propagation.

These classes coordinate miner behaviour, propagation delays, and interactions between local miner views of the DAG."""

from GhostForge_miner_Man import Miner


class MasterMiner(Miner):
    """Encapsulate related simulation state and behaviour for the MasterMiner component."""
    def __init__(self, miner_id, delay_matrix, visualizer):
        """  init   used by the GhostForge research simulation."""
        super().__init__(miner_id, delay_matrix, visualizer)

    def receive_block_immediately(self, block_id, parents):
        """Receive block immediately used by the GhostForge research simulation."""
        if block_id not in self.dag:
            print(f"Master Miner {self.miner_id} received block {block_id} with parents {parents}.")
            self.dag.add_node(block_id)
            for parent in parents:
                self.dag.add_edge(parent, block_id)
            self.apply_protocol()  # Apply protocol on receiving the block
            self.visualize_current_dag(block_id,
                                       "master_after_receiving")  # Visualize the DAG after receiving the block
