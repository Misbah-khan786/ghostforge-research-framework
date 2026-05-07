"""Network and miner models used to simulate distributed block creation and propagation.

These classes coordinate miner behaviour, propagation delays, and interactions between local miner views of the DAG."""

import threading
from threading import Event
import os
import random
import networkx as nx
from DAG.dag_helpers import tips
from GHOSTFORGE.GF_New_JMaxTip_DY_THR import initialize_genesis, apply_ghostforge, update_scores
from Network.Delaymatrix import MinerDelayMatrix
from DAGVisulizer.dagVisulizer_Jmaxtip_DY import DAGVisualizer
from Simulation.order_convergence import (record_orders, update_orders,
                                          check_global_order_convergence, plot_global_convergence,
                                          plot_individual_convergence, check_individual_order_convergence,
                                          calculate_global_locked_prefix_size, calculate_locked_prefix_sizes,
                                          plot_miner_locked_prefix_sizes, plot_global_locked_prefix_size)
import time as time_module
from time import time
import matplotlib.pyplot as plt

def timer_func(func):
    # This function shows the execution time of
    # the function object passed
    """Timer func used by the GhostForge research simulation."""
    def wrap_func(*args, **kwargs):
        """Wrap func used by the GhostForge research simulation."""
        t1 = time()
        result = func(*args, **kwargs)
        t2 = time()
        # print(f'Function {func.__name__!r} executed in {(t2 - t1):.4f}s')
        return result
    return wrap_func


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
        self.previous_max_tip = None  # Add this to store the previous max tip
        self.order_history = []  # Threshold order
        self.stability_count = {}
        self.locked_blocks = set()
        initialize_genesis(self.dag, self.blue_set, self.blue_scores)
        self.blocks_to_send = []
        self.propagation_events = []  # Add this line
        self.receive_counter = 0
        self.last_generation_time = 0
        self.next_generation_time = 0
        self.min_gen_time_ms = 100
        self.max_gen_time_ms = 250

    def update_stability_count(self):
        """Update stability count used by the GhostForge research simulation."""
        if not self.order_history:
            self.order_history.append(self.previous_order)
            return

        previous_order = self.order_history[-1]
        current_order = self.previous_order
        max_prefix_length = min(len(previous_order), len(current_order))

        longest_stable_prefix_length = 0

        for i in range(1, max_prefix_length + 1):
            if current_order[:i] == previous_order[:i]:
                self.stability_count[i] = self.stability_count.get(i, 0) + 1
            else:
                self.stability_count[i] = 0

            if self.stability_count[i] >= 5:
                longest_stable_prefix_length = i

        # Lock the longest stable prefix
        if longest_stable_prefix_length > 0:
            locked_prefix = current_order[:longest_stable_prefix_length]
            print(f"Locking prefix: {locked_prefix} for miner {self.miner_id}")
            for block in locked_prefix:
                self.locked_blocks.add(block)
                self.locked_blocks.update(nx.ancestors(self.dag, block))  # Add all ancestors of the locked blocks
        # # Conflict resolution: Remove conflicting blocks from current_order
        # non_conflicting_order = []
        # for block in current_order:
        #     if block not in previous_order or previous_order.index(block) == current_order.index(block):
        #         non_conflicting_order.append(block)
        #
        # # Update current_order with non-conflicting blocks
        # current_order = non_conflicting_order
        self.order_history.append(current_order)

    @timer_func
    def create_block(self, block_id, parents):
        """Create block used by the GhostForge research simulation."""
        self.dag.add_node(block_id)
        for parent in parents:
            self.dag.add_edge(parent, block_id)
        self.blocks_to_send.append((block_id, parents))

    @timer_func
    def generate_block(self, step):
        """Generate block used by the GhostForge research simulation."""
        current_time = time_module.time()
        if current_time >= self.next_generation_time:
            block_id = f"{self.miner_id}_{step}"
            tips = [node for node in self.dag.nodes if self.dag.out_degree(node) == 0]
            self.create_block(block_id, tips)
            self.apply_protocol()
            self.last_generation_time = current_time
            self.next_generation_time = current_time + random.randint(self.min_gen_time_ms, self.max_gen_time_ms)/ 1000 # Next generation time
        else:
            a=1
            # print(f"Miner {self.miner_id} is waiting to generate the next block.")

    @timer_func
    def receive_block(self, block_id, parents):
        """Receive block used by the GhostForge research simulation."""
        self.receive_counter += 1
        time_module.sleep(random.uniform(5, 7) / 1000)  # Reception handling delay
        if block_id not in self.dag:
            self.dag.add_node(block_id)
            for parent in parents:
                self.dag.add_edge(parent, block_id)
            self.apply_protocol()  # Apply protocol on receiving the block

    def get_ancestry(self, block_id):
        """Recursively get the ancestry of a block."""
        ancestors = set(nx.ancestors(self.dag, block_id))
        ancestry = [(ancestor, list(self.dag.predecessors(ancestor))) for ancestor in ancestors]
        return ancestry

    @timer_func
    def propagate_blocks_with_delay(self, other_miners):
        """Propagate blocks with delay used by the GhostForge research simulation."""
        propagation_events = []
        for block_id, parents in self.blocks_to_send:
            event = Event()
            propagation_events.append(event)
            for miner in other_miners:
                delay = self.delay_matrix.get_delay(self.miner_id, miner.miner_id) / 1000  # Convert ms to seconds
                threading.Timer(delay, self._propagate_block, args=[miner, block_id, parents, event]).start()
        self.blocks_to_send = []
        self.propagation_events.extend(propagation_events)  # Store events for global synchronization

    def _propagate_block(self, miner, block_id, parents, event):
        """ propagate block used by the GhostForge research simulation."""
        miner.receive_block(block_id, parents)
        event.set()

    @timer_func
    def apply_protocol(self):
        """Apply protocol used by the GhostForge research simulation."""
        self.apply_protocol_with_locked_blocks()

    def apply_protocol_with_locked_blocks(self):
        # print(f"Locked blocks before applying protocol: {self.locked_blocks}")
        # If a prefix is locked, treat it and its ancestors as a new genesis block
        """Apply protocol with locked blocks used by the GhostForge research simulation."""
        blocks_to_process = [block for block in self.dag.nodes if block not in self.locked_blocks]
        # print(f"Blocks considered to  protocol which are not ordered/or part of ordered blocks: {blocks_to_process}")


        # Apply the protocol to the remaining blocks
        ordered_list, self.blue_set, self.red_set, self.blue_scores, self.previous_max_tip = apply_ghostforge(
            self.dag,
            blocks_to_process,
            self.blue_set,
            self.red_set,
            self.blue_scores,
            self.visualizer,
            self.previous_order,
            self.miner_id,
            self.previous_max_tip
        )
        # self.previous_order = [block for block in ordered_list if block not in self.locked_blocks]
        locked_ordered_list = [block for block in self.previous_order if block in self.locked_blocks]
        new_ordered_list = [block for block in ordered_list if block not in self.locked_blocks]

        # Combine locked blocks and new blocks while keeping their relative order
        self.previous_order = locked_ordered_list + new_ordered_list
        update_scores(self.dag, self.blue_set, self.red_set, self.blue_scores)

        # Update stability count after applying the protocol
        self.update_stability_count()
        # print(f"New order after applying protocol: {self.previous_order}")

    def visualize_current_dag(self, block_id=None, context=""):
        """Visualize current dag used by the GhostForge research simulation."""
        label = f'graph_{self.miner_id}'
        if context:
            label += f'_{context}'
        if block_id:
            label += f'_{block_id}'

        output_dir = f'DY_NMax_TIpoutput_directory/{self.miner_id}'
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f'{label}.gv')
        try:
            self.visualizer.visualize_dag(dag=self.dag, blue_set=self.blue_set, red_set=self.red_set,
                                          blue_scores=self.blue_scores, output_path=output_path,
                                          order_list=self.previous_order)
        except Exception as e:
            pass

    def run(self, t):
        """Run used by the GhostForge research simulation."""
        if t == 0:
            return
        if random.random() < 0.9:  # Adjust probability as needed
            self.generate_block(t)  # Call generate_block which handles block creation and protocol application
        self.visualizer.print_scores_and_order(self.previous_order)


class MasterMiner(Miner):
    """Encapsulate related simulation state and behaviour for the MasterMiner component."""
    def __init__(self, miner_id, delay_matrix, visualizer):
        """  init   used by the GhostForge research simulation."""
        super().__init__(miner_id, delay_matrix, visualizer)

    @timer_func
    def receive_block_immediately(self, block_id, parents):
        """Receive block immediately used by the GhostForge research simulation."""
        if block_id not in self.dag:
            self.dag.add_node(block_id)
            for parent in parents:
                self.dag.add_edge(parent, block_id)
            self.apply_protocol()  # Apply protocol on receiving the block


def simulate_miners(miners, master_miner, num_time_steps, step_duration_ms, generate_prob=0.9):
    """Simulate miners used by the GhostForge research simulation."""
    miner_orders = record_orders(miners)  # Initialize order recording
    order_history = []
    locked_blocks_history = []
    miner_locked_prefix_sizes = {miner.miner_id: [] for miner in miners}

    for t in range(1, num_time_steps + 1):
        start_time = time_module.time()
        print(f"\nStep {t}:")

        # Determine which miners will generate blocks at this step
        generating_miners = [miner for miner in miners if random.random() < generate_prob]

        # Ensure at least one miner generates a block at each step
        if not generating_miners:
            generating_miners = [random.choice(miners)]

        threads = []
        for miner in generating_miners:
            thread = threading.Thread(target=miner.generate_block, args=(t,))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()

        # Master miner receives all blocks created at this step
        for miner in generating_miners:
            for block_id, parents in miner.blocks_to_send:
                master_miner.receive_block_immediately(block_id, parents)

        # Dynamic block propagation
        for miner in miners:
            miner.propagate_blocks_with_delay([m for m in miners if m != miner])

        # Update orders after each step
        update_orders(miner_orders, miners)
        order_history.append({miner.miner_id: miner.previous_order.copy() for miner in miners})
        locked_blocks_history.append({miner.miner_id: set(miner.locked_blocks) for miner in miners})

        # Track locked prefix sizes for each miner
        for miner in miners:
            locked_blocks = locked_blocks_history[-1][miner.miner_id]
            locked_prefix_size = len([block for block in miner.previous_order if block in locked_blocks])
            miner_locked_prefix_sizes[miner.miner_id].append(locked_prefix_size)

        # Ensure each step takes at least step_duration milliseconds
        elapsed_time = time_module.time() - start_time
        elapsed_time_ms = elapsed_time * 1000  # Convert to seconds
        if elapsed_time_ms < step_duration_ms:
            time_module.sleep((step_duration_ms - elapsed_time_ms) / 1000)  # Convert to seconds

    # Ensure locked_blocks_history and miner_orders have the same length
    while len(locked_blocks_history) < len(next(iter(miner_orders.values()))):
        locked_blocks_history.append({miner.miner_id: set(miner.locked_blocks) for miner in miners})

    # Wait for all propagation events to complete before finishing simulation
    for miner in miners:
        for event in miner.propagation_events:
            event.wait()

    # Calculate locked prefix sizes
    global_locked_prefix_sizes = calculate_global_locked_prefix_size(miner_orders, locked_blocks_history)
    # for prefix in global_locked_prefix_sizes:
    #     print(f" Common Prefix: {prefix}")

    # Ensure directory exists for locked prefixes
    locked_prefix_dir = 'plot_locked_prefixes-SC7'
    if not os.path.exists(locked_prefix_dir):
        os.makedirs(locked_prefix_dir)

    plot_miner_locked_prefix_sizes(miner_locked_prefix_sizes, locked_prefix_dir)
    plot_global_locked_prefix_size(global_locked_prefix_sizes, locked_prefix_dir)

    # Check for convergence
    common_prefixes = check_global_order_convergence(miner_orders)
    individual_convergence = check_individual_order_convergence(miner_orders)

    # Print the common prefixes at each step
    for step, prefix in common_prefixes:
        print(f"Step {step}: Common Prefix: {prefix}")

    output_dir = 'plot Convergence_SC7'

    # Call the plot functions
    plot_global_convergence(common_prefixes, output_dir)
    plot_individual_convergence(individual_convergence, output_dir)



if __name__ == "__main__":
    miners_ids = ['M1', 'M2', 'M3', 'M4']
    miner_delay_matrix = MinerDelayMatrix()
    master_miner_id = 'Master'

    # Initialize the visualizer and define the miners
    visualizer = DAGVisualizer()
    miners = [Miner(miner_id, miner_delay_matrix, visualizer) for miner_id in miners_ids]
    master_miner = MasterMiner(master_miner_id, miner_delay_matrix, visualizer)

    # Define the number of time steps for the simulation
    num_time_steps =40
    step_duration_ms =20 # Step duration in milliseconds

    simulate_miners(miners, master_miner, num_time_steps, step_duration_ms)

