"""Network and miner models used to simulate distributed block creation and propagation.

These classes coordinate miner behaviour, propagation delays, and interactions between local miner views of the DAG."""

import threading
import networkx as nx
from DAG.dag_helpers import tips
from GHOSTFORGE.GhostForgeDy import initialize_genesis, apply_J_version, update_scores
from Network.Delaymatrix import MinerDelayMatrix  # Assuming you have the MinerDelayMatrix class in a separate file
from DAGVisulizer.dagvisualizerDy import DAGVisualizer


class Miner:
    """Encapsulate related simulation state and behaviour for the Miner component."""
    def __init__(self, miner_id, delay_matrix, visualizer):
        """  init   used by the GhostForge research simulation."""
        self.miner_id = miner_id
        self.delay_matrix = delay_matrix
        self.dag = nx.DiGraph()
        self.blue_set = set()
        self.red_set = set()
        self.blue_scores = {}
        self.visualizer = visualizer
        self.previous_order = ['G']
        initialize_genesis(self.dag, self.blue_set, self.blue_scores)
        print(f"Miner {self.miner_id} initialized with Genesis block.")
        self.blocks_to_send = []

    def create_block(self, block_id, parents):
        """Create block used by the GhostForge research simulation."""
        print(f"Miner {self.miner_id} created block {block_id} with parents {parents}.")
        self.dag.add_node(block_id)
        for parent in parents:
            self.dag.add_edge(parent, block_id)
        self.blocks_to_send.append((block_id, parents))

    def receive_block(self, block_id, parents):
        """Receive block used by the GhostForge research simulation."""
        if block_id not in self.dag:
            print(f"Miner {self.miner_id} received block {block_id} with parents {parents}.")
            self.dag.add_node(block_id)
            for parent in parents:
                self.dag.add_edge(parent, block_id)
            self.apply_protocol()  # Apply protocol on receiving the block
            self.visualize_current_dag(block_id, "after_receiving")  # Visualize the DAG after receiving the block

    def get_ancestry(self, block_id):
        """Recursively get the ancestry of a block."""
        ancestors = set(nx.ancestors(self.dag, block_id))
        ancestry = [(ancestor, list(self.dag.predecessors(ancestor))) for ancestor in ancestors]
        return ancestry

    def propagate_blocks(self, other_miners):
        """Propagate blocks used by the GhostForge research simulation."""
        for block_id, parents in self.blocks_to_send:
            ancestry = self.get_ancestry(block_id)
            ancestry.append((block_id, parents))  # Include the block itself
            for miner in other_miners:
                for ancestor_id, ancestor_parents in ancestry:
                    miner.receive_block(ancestor_id, ancestor_parents)
        self.blocks_to_send = []

    def apply_protocol(self):
        """Apply protocol used by the GhostForge research simulation."""
        print(f"Miner {self.miner_id} is applying the protocol.")
        ordered_list, self.blue_set, self.red_set, self.blue_scores = apply_J_version(
            self.dag,
            list(self.dag.nodes),
            self.blue_set,
            self.red_set,
            self.blue_scores,
            self.visualizer,
            self.previous_order
        )
        self.previous_order = ordered_list
        update_scores(self.dag, self.blue_set, self.red_set, self.blue_scores)

    def visualize_current_dag(self, block_id=None, context=""):
        """Visualize current dag used by the GhostForge research simulation."""
        label = f'graph_{self.miner_id}'
        if context:
            label += f'_{context}'
        if block_id:
            label += f'_{block_id}'
        output_path = f'output_directory/{label}'
        self.visualizer.visualize_dag(dag=self.dag, blue_set=self.blue_set, red_set=self.red_set, blue_scores=self.blue_scores, output_path=output_path, order_list=self.previous_order)

    def run(self, steps, t):
        """Run used by the GhostForge research simulation."""
        if t == 0:
            return
        print(f"Miner {self.miner_id} at time step t{t}.")
        for block_id, parents in steps[t]:
            # Check if the miner is supposed to create this block
            if (self.miner_id, block_id) in miner_block_mapping[t]:
                self.create_block(block_id, parents)
                print(f"Miner {self.miner_id} is processing block {block_id}.")
                self.apply_protocol()
        self.visualizer.print_scores_and_order(self.previous_order)
        self.visualize_current_dag(context="after_creation")
        print(f"Miner {self.miner_id} Blue Set: {self.blue_set}")
        print(f"Miner {self.miner_id} Red Set: {self.red_set}")
        print(f"Miner {self.miner_id} Tips: {tips(self.dag)}")


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
            self.visualize_current_dag(block_id, "master_after_receiving")  # Visualize the DAG after receiving the block


def simulate_miners(miners, master_miner, steps):
    """Simulate miners used by the GhostForge research simulation."""
    delay_matrix = MinerDelayMatrix()

    for t in range(len(steps)):
        if t == 0:
            continue
        input(f"Press Enter to proceed to time step t{t}...")
        print(f"\nStep {t}:")
        threads = []
        for miner in miners:
            thread = threading.Thread(target=miner.run, args=(steps, t))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()

        # Master miner receives all blocks created at this step
        for miner in miners:
            for block_id, parents in steps[t]:
                if (miner.miner_id, block_id) in miner_block_mapping[t]:
                    master_miner.receive_block_immediately(block_id, parents)

        # Visualize the DAG for each miner after block creation and protocol application
        for miner in miners:
            miner.visualize_current_dag(context=f"t{t}_after_creation")

        input(f"Start Propagation at time step t{t}...")

        # Handle block propagation between steps
        for sender_id in range(len(miners)):
            for receiver_id in range(len(miners)):
                if sender_id != receiver_id:
                    delay = delay_matrix.get_delay(sender_id, receiver_id)
                    threading.Timer(delay, miners[sender_id].propagate_blocks, args=([miners[receiver_id]],)).start()

        input(f"Press Enter to continue after block propagation at time step t{t}...")

        # Visualize the DAG for each miner after block propagation
        for miner in miners:
            miner.visualize_current_dag(context=f"t{t}_after_propagation")
        master_miner.visualize_current_dag(context=f"t{t}_after_propagation")


if __name__ == "__main__":
    miners_ids = ['M1', 'M2', 'M3', 'M4']
    miner_delay_matrix = MinerDelayMatrix()
    master_miner_id = 'Master'

    # Initialize the visualizer and define the miners
    visualizer = DAGVisualizer()
    miners = [Miner(miner_id, miner_delay_matrix, visualizer) for miner_id in miners_ids]
    master_miner = MasterMiner(master_miner_id, miner_delay_matrix, visualizer)

    # Dynamically add blocks
    for t in range(1, 5):
        new_blocks = visualizer.add_batch_of_blocks(miners[0].dag, num_blocks=4, max_parents=3)
        for block_id in new_blocks:
            for miner in miners:
                miner.receive_block(block_id, list(miners[0].dag.predecessors(block_id)))

    # Simulate miners with the dynamically created steps
    simulate_miners(miners, master_miner, visualizer.steps)
