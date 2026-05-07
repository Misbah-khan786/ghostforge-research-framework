"""Visualisation helpers for inspecting DAG construction, block colouring, ordering, and protocol behaviour.

These utilities support debugging and presentation of simulation states."""

import os
from graphviz import Digraph
import networkx as nx

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
        """Add blocks step by step used by the GhostForge research simulation."""
        self.steps = [
            [('G', [])],  # t0: Genesis block, everyone has this
            [('B', ['G']), ('C', ['G']), ('D', ['G']), ('E', ['G'])],
            # t1: M1 creates B, M2 creates C, M3 creates D, M4 creates E
            [('F', ['B', 'C']), ('H', ['C', 'D', 'E']), ('I', ['E'])],  # t2: M2 creates F, M3 creates H, M4 creates I
            [('J', ['F', 'H']), ('K', ['B', 'H', 'I']), ('L', ['D', 'I'])],
            # t3: M1 creates J, M3 creates K, M4 creates L
            [('M', ['F', 'K'])]  # t4: M1 creates M
        ]

    def add_block(self, node, edges):
        """Add block used by the GhostForge research simulation."""
        self.dag.add_node(node)
        for edge in edges:
            self.dag.add_edge(edge, node)


    def print_scores_and_order(self, ordered_list):
        """Print scores and order used by the GhostForge research simulation."""
        print("\nOrder of Nodes:")
        print(ordered_list)



    def visualize_dag(self, dag, blue_set, red_set, blue_scores, output_path='NMax_TIpoutput_directory/graph_output',
                      order_list=None):
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
            order_str = ""
            for node in order_list:
                if node in blue_set:
                    order_str += f'<FONT COLOR="blue">{node}</FONT>, '
                else:
                    order_str += f'<FONT COLOR="red">{node}</FONT>, '
            order_str = order_str.rstrip(', ')

            with dot.subgraph(name='cluster_order') as s:
                s.attr(rankdir='TB')
                s.node("Order", label=f"<<b>Order:</b> {order_str}>", shape='plaintext')
                #s.attr(label="Order")
        try:
            dot.render(output_path, format='png', view=False)  # Specify format and set view to False
            # print(f"Graph successfully rendered and saved to {output_path}.png")
        except Exception as e:
            print(f"Error rendering graph: {e}")