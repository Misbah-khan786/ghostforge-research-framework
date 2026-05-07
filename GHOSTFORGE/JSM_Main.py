"""GhostForge consensus and ordering algorithms.

This module contains research implementations of block colouring, scoring, tip selection, and ordering variants evaluated during the PhD research."""

import os
import networkx as nx
from graphviz import Digraph
from DAG.dag_helpers import tips, block_details
from GHOSTFORGE.JSM_Version import  initialize_genesis, apply_J_version, update_scores

class DAGVisualizer:
    """Encapsulate related simulation state and behaviour for the DAGVisualizer component."""
    def __init__(self):
        """  init   used by the GhostForge research simulation."""
        self.dag = nx.DiGraph()
        self.blue_scores = {}
        self.blue_set = set()
        self.red_set = set()
        self.steps = []


    def add_blocks_step_by_step(self):
        # Define steps for adding blocks
        """Add blocks step by step used by the GhostForge research simulation."""
        self.steps = [
            [('Genesis', [])],  # t0: Genesis block
            [('B', ['Genesis']), ('C', ['Genesis']), ('D', ['Genesis']), ('E', ['Genesis'])],  # t1: Blocks B, C, D, E referring to Genesis
            [('F', ['B', 'C']), ('H', ['C', 'D', 'E']), ('I', ['E'])],  # t2: Blocks F, H, I
            [('J', ['F', 'H']), ('K', ['B', 'H', 'I']), ('L', ['D', 'I'])],  # t3: Blocks J, K, L
            [('M', ['F', 'K'])] # t4: Block M

        ]


    def add_block(self, node, edges):
        """Add a single block to the DAG"""
        self.dag.add_node(node)
        for edge in edges:
            self.dag.add_edge(edge, node)

    def visualize_dag(self, step=None):
        """Visualize dag used by the GhostForge research simulation."""
        os.environ["PATH"] += os.pathsep + 'C:/Program Files/Graphviz/bin/'
        dot = Digraph(engine="dot")
        dot.attr(rankdir='LR')
        dot.attr('node', shape='box', width='0.5', height='0.5')

        for i, step_blocks in enumerate(self.steps):
            if step is not None and i > step:
                break
            for node, edges in step_blocks:
                self.add_block(node, edges)
                label = f"{node}\n{self.blue_scores.get(node, '')}"
                if node in self.blue_set:
                    dot.node(node, label=label, style='filled', fillcolor='#ADD8E6 ', color='blue', shape='box')
                else:
                    dot.node(node, label=label, style='filled', fillcolor='lightcoral', color='red', shape='box')
                for edge in edges:
                    dot.edge(edge, node, dir='back', arrowtail='normal', arrowsize='0.5')

        output_path = '../output_directory/graph_output'
        dot.render(output_path, view=True)

    def visualize_dag_after_block_level(self, block, B_blue_set, B_red_set, B_blue_scores):
        """Visualize the DAG after block-level coloring and scoring for the specified block."""
        os.environ["PATH"] += os.pathsep + 'C:/Program Files/Graphviz/bin/'
        dot = Digraph(engine="dot")
        dot.attr(rankdir='LR')
        dot.attr('node', shape='box', width='0.5', height='0.5')

        for node in self.dag.nodes:
            label = f"{node}\n{B_blue_scores.get(node, '')}"
            if node in B_blue_set:
                # Node is in the blue set
                dot.node(node, label=label, style='filled', fillcolor='white', color='blue', shape='box')
            elif node in B_red_set:
                # Node is in the red set
                dot.node(node, label=label, style='filled', fillcolor='lightcoral', color='red', shape='box')
            else:
                # Default to light blue for other nodes
                dot.node(node, label=label, style='filled', fillcolor='#ADD8E6', color='grey', shape='box')

            for edge in self.dag.predecessors(node):
                dot.edge(edge, node, dir='back', arrowtail='normal', arrowsize='0.5')

        output_path = f'output_directory/graph_output_after_{block}'
        dot.render(output_path, view=True)
    def show_block_details(self, block_name):
        """Show block details used by the GhostForge research simulation."""
        block_details(self.dag, block_name)

    def print_scores_and_order(self, ordered_list):
        """Print scores and order used by the GhostForge research simulation."""
        print("Scores of Nodes:")
        for node in self.dag.nodes:
            print(f"Node: {node}, Score: {self.blue_scores.get(node, 'N/A')}")
        print("\nOrder of Nodes:")
        print(ordered_list)


visualizer = DAGVisualizer()

visualizer.add_blocks_step_by_step()

# Initialize Genesis block
initialize_genesis(visualizer.dag, visualizer.blue_set, visualizer.blue_scores)

previous_order = ['Genesis']  # Initial order starts with Genesis

for step in range(1, len(visualizer.steps)):  # Start from 1 since Genesis is already added
    for node, edges in visualizer.steps[step]:
        visualizer.add_block(node, edges)

    # Apply J_version strategy and recolor tips
    ordered_list, blue_set, red_set, blue_scores = apply_J_version(
        visualizer.dag,
        [node for node, _ in visualizer.steps[step]],
        visualizer.blue_set,
        visualizer.red_set,
        visualizer.blue_scores,
        visualizer,
        previous_order
    )

    visualizer.blue_set = blue_set
    visualizer.red_set = red_set
    visualizer.blue_scores = blue_scores
    previous_order = ordered_list  # Update previous_order for the next step

    # Update scores after DAG-level coloring and ordering
    update_scores(visualizer.dag, visualizer.blue_set, visualizer.red_set, visualizer.blue_scores)

    visualizer.visualize_dag(step=step)
    visualizer.print_scores_and_order(ordered_list)

    print(f"Blue Set at Step {step}: {blue_set}")
    print(f"Red Set at Step {step}: {red_set}")
    print(f"Tips at Step {step}: {tips(visualizer.dag)}")
    input("^^^^Press Enter to continue to the next step...")