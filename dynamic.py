"""Example dynamic simulation runner for the GhostForge research prototype.

This script wires together DAG, network, miner, and consensus components for experimental simulation runs."""

import os
import networkx as nx
from graphviz import Digraph
import random
from DAG.dag_helpers import tips, block_details
from OG_J_Version.J_version import initialize_genesis, apply_J_version


class DAGVisualizer:
    """Encapsulate related simulation state and behaviour for the DAGVisualizer component."""
    def __init__(self):
        """  init   used by the GhostForge research simulation."""
        self.dag = nx.DiGraph()
        self.blue_scores = {}
        self.blue_set = set()
        self.red_set = set()

    def add_blocks_automatically(self, num_blocks_per_step, max_parents, malicious_ratio=0.0):
        """
        Automatically add blocks to the DAG.
        """
        last_block_num = max([int(node.replace('B', '')) for node in self.dag.nodes if node.startswith('B')], default=0)
        new_blocks = []

        num_malicious_blocks = int(num_blocks_per_step * malicious_ratio)

        # Identify if it's the first batch
        is_first_batch = 'Genesis' in self.dag.nodes and all(self.dag.in_degree(n) == 0 for n in self.dag.nodes)

        for i in range(1, num_blocks_per_step + 1):
            new_block_name = f'B{last_block_num + i}'
            self.dag.add_node(new_block_name)
            new_blocks.append(new_block_name)

            # Determine if the block is malicious or not
            is_malicious = i <= num_malicious_blocks

            if is_first_batch:
                # Connect only to 'Genesis' if it's the first batch
                parents = ['Genesis']
            else:
                current_tips = [node for node in self.dag.nodes if self.dag.out_degree(node) == 0]
                if is_malicious:
                    num_parents = max(1, max_parents // 2)  # Malicious blocks have fewer parents
                else:
                    num_parents = random.randint(1, min(len(current_tips), max_parents)) if current_tips else 0
                parents = random.sample(current_tips, num_parents) if current_tips else []

            for parent in parents:
                self.dag.add_edge(parent, new_block_name)

        return new_blocks

    def visualize_dag(self, step=None):
        """Visualize dag used by the GhostForge research simulation."""
        os.environ["PATH"] += os.pathsep + 'C:/Program Files/Graphviz/bin/'
        dot = Digraph(engine="dot")
        dot.attr(rankdir='LR')
        dot.attr('node', shape='box', width='0.5', height='0.5')

        for node in self.dag.nodes:
            label = f"{node}\n{self.blue_scores.get(node, '')}"
            if node in self.blue_set:
                dot.node(node, label=label, style='filled', fillcolor='#ADD8E6 ', color='blue', shape='box')
            else:
                dot.node(node, label=label, style='filled', fillcolor='lightcoral', color='red', shape='box')
            for edge in self.dag.predecessors(node):
                dot.edge(edge, node, dir='back', arrowtail='normal', arrowsize='0.5')

        output_path = f'output_directory/graph_output_step_{step}' if step else 'output_directory/graph_output'
        dot.render(output_path, view=True)

    def show_block_details(self, block_name):
        """Show block details used by the GhostForge research simulation."""
        block_details(self.dag, block_name)

    def print_scores_and_order(self, ordered_list):
        """Print scores and order used by the GhostForge research simulation."""
        print("\nOrder of Nodes:")
        print(ordered_list)

if __name__ == "__main__":
    visualizer = DAGVisualizer()

    initialize_genesis(visualizer.dag, visualizer.blue_set, visualizer.blue_scores)
    num_steps = 5
    num_blocks_per_step = 4
    max_parents = 3
    malicious_ratio = 0.2

    for step in range(1, num_steps + 1):
        print(f"\n--- Step {step} ---")
        new_blocks = visualizer.add_blocks_automatically(num_blocks_per_step, max_parents, malicious_ratio)
        print(f"New blocks added: {new_blocks}")

        # Apply J_version strategy to the new blocks
        ordered_list, blue_set, red_set, blue_scores = apply_J_version(
            visualizer.dag,
            new_blocks,
            visualizer.blue_set,
            visualizer.red_set,
            visualizer.blue_scores,
            visualizer
        )

        # Update internal sets and scores
        visualizer.blue_set = blue_set
        visualizer.blue_scores = blue_scores
        visualizer.red_set = red_set

        # Optionally visualize or perform further processing
        visualizer.visualize_dag(step=step)
        visualizer.print_scores_and_order(ordered_list)

        print(f"Blue Set at Step {step}: {blue_set}")
        print(f"Red Set at Step {step}: {red_set}")
        print(f"Tips after step {step}: {tips(visualizer.dag)}")
        input("Press Enter to continue to the next step...")
