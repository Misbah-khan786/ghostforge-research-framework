"""Network and miner models used to simulate distributed block creation and propagation.

These classes coordinate miner behaviour, propagation delays, and interactions between local miner views of the DAG."""

import threading
from threading import Event
import os
import random
import networkx as nx
from DAG.dag_helpers import tips
from GHOSTFORGE.GF_New_JMaxTip_DY  import initialize_genesis, apply_ghostforge, update_scores
from Network.Delaymatrix import MinerDelayMatrix  # Assuming you have the MinerDelayMatrix class in a separate file
from DAGVisulizer.dagVisulizer_Jmaxtip_DY import DAGVisualizer
from Simulation.order_convergence import (record_orders, update_orders,
                                          check_global_order_convergence, plot_global_convergence,
                                          plot_individual_convergence, check_individual_order_convergence)
import time as time_module
from time import time


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
        initialize_genesis(self.dag, self.blue_set, self.blue_scores)
        # #print(f"Miner {self.miner_id} initialized with Genesis block.")
        self.blocks_to_send = []
        self.propagation_events = []  # Add this line
        self.receive_counter = 0
        self.last_generation_time = 0
        self.next_generation_time = 0
        self.min_gen_time_ms = 0
        self.max_gen_time_ms = 1

    @timer_func
    def create_block(self, block_id, parents):
        # #print(f"Miner {self.miner_id} created block {block_id} with parents {parents}.")

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
            # print(f"Miner {self.miner_id} generated block {block_id} at time step {time_step}.")
            self.last_generation_time = current_time
            self.next_generation_time = current_time + random.randint(self.min_gen_time_ms, self.max_gen_time_ms)  # Next generation time
        else:
              print(f"Miner {self.miner_id} is waiting to generate the next block.")

    @timer_func
    def receive_block(self, block_id, parents):
        """Receive block used by the GhostForge research simulation."""
        self.receive_counter += 1
        # print(f"{self.miner_id} receive_block: receiveCounter {self.receive_counter}")
        time_module.sleep(random.uniform(5, 7) / 1000)  # Reception handling delay
        if block_id not in self.dag:
            # #print(f"Miner {self.miner_id} received block {block_id} with parents {parents}.")
            self.dag.add_node(block_id)
            for parent in parents:
                self.dag.add_edge(parent, block_id)
            self.apply_protocol()  # Apply protocol on receiving the block
            # self.visualize_current_dag(block_id, "after_receiving")  # Visualize the DAG after receiving the block

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
        # print(f"{self.miner_id} propagate_block to {miner.miner_id}")
        """ propagate block used by the GhostForge research simulation."""
        miner.receive_block(block_id, parents)
        event.set()

    @timer_func
    def apply_protocol(self):
        #print(f"Miner {self.miner_id} is applying the protocol.")
        """Apply protocol used by the GhostForge research simulation."""
        ordered_list, self.blue_set, self.red_set, self.blue_scores, self.previous_max_tip  = apply_ghostforge(
            self.dag,
            list(self.dag.nodes),
            self.blue_set,
            self.red_set,
            self.blue_scores,
            self.visualizer,
            self.previous_order,
            self.miner_id,
            self.previous_max_tip
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

        output_dir = f'DY_NMax_TIpoutput_directory/{self.miner_id}'
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f'{label}.gv')
        try:
            self.visualizer.visualize_dag(dag=self.dag, blue_set=self.blue_set, red_set=self.red_set,
                                          blue_scores=self.blue_scores, output_path=output_path,
                                          order_list=self.previous_order)
        except Exception as e:
            pass
            #print(f"Error rendering graph: {e}")

    def run(self, t):
        """Run used by the GhostForge research simulation."""
        if t == 0:
            return
        #print(f"Miner {self.miner_id} at time step t{t}.")

        if random.random() < 0.5:  # Adjust probability as needed
            self.generate_block(t)  # Call generate_block which handles block creation and protocol application

        self.visualizer.print_scores_and_order(self.previous_order)
        #print(f"Miner {self.miner_id} Blue Set: {self.blue_set}")
        #print(f"Miner {self.miner_id} Red Set: {self.red_set}")
        #print(f"Miner {self.miner_id} Tips: {tips(self.dag)}")



class MasterMiner(Miner):
    """Encapsulate related simulation state and behaviour for the MasterMiner component."""
    def __init__(self, miner_id, delay_matrix, visualizer):
        """  init   used by the GhostForge research simulation."""
        super().__init__(miner_id, delay_matrix, visualizer)

    @timer_func
    def receive_block_immediately(self, block_id, parents):
        """Receive block immediately used by the GhostForge research simulation."""
        if block_id not in self.dag:
            #print(f"Master Miner {self.miner_id} received block {block_id} with parents {parents}.")
            self.dag.add_node(block_id)
            for parent in parents:
                self.dag.add_edge(parent, block_id)
            self.apply_protocol()  # Apply protocol on receiving the block
            # self.visualize_current_dag(block_id, "master_after_receiving")  # Visualize the DAG after receiving the block


def simulate_miners(miners, master_miner, num_time_steps, step_duration_ms, generate_prob=0.9):
    """Simulate miners used by the GhostForge research simulation."""
    miner_orders = record_orders(miners)  # Initialize order recording
    for t in range(1, num_time_steps + 1):
        startTime = time_module.time()
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

        # # Visualize the DAG for each miner after block creation and protocol application
        # for miner in miners:
        #     miner.visualize_current_dag(context=f"t{t}_after_creation")

        # Dynamic block propagation
        for miner in miners:
            miner.propagate_blocks_with_delay([m for m in miners if m != miner])

        # # Visualize the DAG for each miner after block propagation
        # for miner in miners:
        #     miner.visualize_current_dag(context=f"t{t}_after_propagation")
        #
        # master_miner.visualize_current_dag(context=f"t{t}_after_propagation")

        # # Update orders after each step
        update_orders(miner_orders, miners)


        # Ensure each step takes at least step_duration seconds
        elapsed_time = time_module.time() - startTime
        elapsed_time_ms = elapsed_time * 1000  # Convert to milliseconds
        # Ensure each step takes at least step_duration_ms milliseconds
        if elapsed_time_ms < step_duration_ms:
            time_module.sleep((step_duration_ms - elapsed_time_ms) / 1000)  # Convert to seconds

    # Wait for all propagation events to complete before finishing simulation
    for miner in miners:
        for event in miner.propagation_events:
            event.wait()

    # Check for convergence
    # partial_convergence = check_partial_order_convergence(miner_orders) global_convergence_step, longest_common_prefix,
    common_prefixes = check_global_order_convergence(miner_orders)
    individual_convergence = check_individual_order_convergence(miner_orders)

    # Print the common prefixes at each step
    #print("Common Prefixes at Each Step:")
    for step, prefix in common_prefixes:
        print(f"Step {step}: Common Prefix: {prefix}")

    output_dir = 'H_JMAX_global_individual_convergence'

    # Call the plot functions
    plot_global_convergence(common_prefixes, output_dir)
    plot_individual_convergence(individual_convergence, output_dir)

## generate random number between 0 and 100 (uniform distribution)
# import random
# 100*random.random()

if __name__ == "__main__":
    miners_ids = ['M1', 'M2', 'M3', 'M4']
    miner_delay_matrix = MinerDelayMatrix()
    master_miner_id = 'Master'

    # Initialize the visualizer and define the miners
    visualizer = DAGVisualizer()
    # visualizer.add_blocks_step_by_step(num_time_steps=5, num_blocks_per_step=4, max_parents=3)  # Example configuration
    miners = [Miner(miner_id, miner_delay_matrix, visualizer) for miner_id in miners_ids]
    master_miner = MasterMiner(master_miner_id, miner_delay_matrix, visualizer)

    # Get the steps from the visualizer
    # Define the number of time steps for the simulation
    num_time_steps = 50
    steps = visualizer.steps
    step_duration_ms  = 90 # Step duration in milliseconds

    simulate_miners(miners, master_miner, num_time_steps, step_duration_ms )


