"""Visualisation helpers for inspecting DAG construction, block colouring, ordering, and protocol behaviour.

These utilities support debugging and presentation of simulation states."""

import os
from graphviz import Digraph
import random

class DAGVisualizer:
    """Encapsulate related simulation state and behaviour for the DAGVisualizer component."""
    def __init__(self):
        """  init   used by the GhostForge research simulation."""
        self.steps = []

    def add_batch_of_blocks(self, dag, num_blocks, max_parents, malicious_ratio=0.0):
        """Add batch of blocks used by the GhostForge research simulation."""
        last_block_num = max([int(node.replace('B', '')) for node in dag.nodes if 'B' in node], default=0)
        new_blocks = []  # to get the blocks of current batch
        # Identify the blocks from the most recent batch and current tips
        recent_blocks = [f'B{i}' for i in range(last_block_num - max_parents + 1, last_block_num + 1) if
                         f'B{i}' in dag.nodes]
        current_tips = [node for node in dag.nodes if dag.out_degree(node) == 0 and node.startswith('B')]

        # Combine recent blocks and current tips to form the pool of potential parents
        potential_parents = list(set(recent_blocks + current_tips))

        num_malicious_blocks = int(num_blocks * malicious_ratio)

        for i in range(1, num_blocks + 1):
            new_block_name = f'B{last_block_num + i}'
            dag.add_node(new_block_name)
            new_blocks.append(new_block_name)

            # If there are not enough potential parents, include genesis or other earlier blocks
            if len(potential_parents) < max_parents:
                additional_parents = [node for node in dag.nodes if dag.in_degree(node) == 0 and node != new_block_name]
                potential_parents.extend(additional_parents)
            # Determine the number of parents for this block
            if i <= num_malicious_blocks:
                # Malicious block with fewer parents
                num_parents = num_blocks // 2
            else:
                # Normal block
                if len(potential_parents) >= max_parents-1:
                    num_parents = random.randint(max_parents-1, min(len(potential_parents), max_parents))
                else:
                    num_parents = len(potential_parents)

            # Randomly select parents for the new block
            parents = random.sample(potential_parents, num_parents) if potential_parents else []

            # Add edges from selected parent blocks to the new block
            for parent in parents:
                dag.add_edge(parent, new_block_name)

        return new_blocks

    def visualize_dag(self, dag, blue_set, red_set, blue_scores, output_path='output_directory/graph_output', order_list=None):
        """Visualize dag used by the GhostForge research simulation."""
        os.environ["PATH"] += os.pathsep + 'C:/Program Files/Graphviz/bin/'
        dot = Digraph(engine="dot")
        dot.attr(rankdir='LR')
        dot.attr('node', shape='box', width='0.5', height='0.5')

        for node in dag.nodes:
            label = f"{node}\n{blue_scores.get(node, '')}"
            if node in blue_set:
                dot.node(node, label=label, style='filled', fillcolor='#ADD8E6', color='blue', shape='box')
            else:
                dot.node(node, label=label, style='filled', fillcolor='lightcoral', color='red', shape='box')
            for parent in dag.predecessors(node):
                dot.edge(parent, node, dir='back', arrowtail='normal', arrowsize='0.5')

        if order_list:
            with dot.subgraph() as s:
                s.attr(rankdir='TB')
                order_label = ", ".join(order_list)
                s.node("Order", label=f"Order: {order_label}", shape='plaintext', width='0.0', height='0.0')

        try:
            dot.render(output_path, view=True)  # Change view to True to display the graph
        except Exception as e:
            print(f"Error rendering graph: {e}")

    def print_scores_and_order(self, ordered_list):
        """Print scores and order used by the GhostForge research simulation."""
        print("\nOrder of Nodes:")
        print(ordered_list)
