"""DAG utility functions used by the GhostForge simulation framework.

This module provides graph-theoretic helpers for querying past sets, tips, anticones, and block scores in a directed acyclic graph (DAG)."""

import networkx as nx

def past(dag, block):
    """Return the set of past blocks for the given block in the DAG."""
    return nx.ancestors(dag, block)

def tips(dag):
    """Return the set of tips (blocks with no children) in the DAG."""
    return {node for node in dag.nodes if dag.out_degree(node) == 0}

def anticone(dag, block):
    """Return the set of blocks that are neither ancestors nor descendants of the given block."""
    past_blocks = past(dag, block)
    future_blocks = nx.descendants(dag, block)
    return {node for node in dag.nodes if node not in past_blocks and node not in future_blocks and node != block}

def score(dag, block, blue_set):
    """Compute the score of the block based on the number of blue blocks in its past."""
    past_blocks = past(dag, block)
    blue_blocks_in_past = [b for b in past_blocks if b in blue_set]
    return len(blue_blocks_in_past) + 1  # Plus one if the block itself is blue

def block_details(dag, block_name):
    """Print details of a given block."""
    print(f"Block: {block_name}")
    print(f"Parents: {list(dag.predecessors(block_name))}")
    print(f"Children: {list(dag.successors(block_name))}")
