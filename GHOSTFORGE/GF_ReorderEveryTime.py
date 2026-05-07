"""GhostForge consensus and ordering algorithms.

This module contains research implementations of block colouring, scoring, tip selection, and ordering variants evaluated during the PhD research."""

import networkx as nx
from DAG.dag_helpers import anticone, past, tips

def initialize_genesis(dag, blue_set, blue_scores):
    """Initialize the Genesis block."""
    dag.add_node('G')  # Add Genesis block to DAG
    blue_set.add('G')  # Add Genesis block to the blue set
    blue_scores['G'] = 1  # Set the initial score for the Genesis block

def block_level_coloring_and_scoring(dag, block, red_set, blue_set, blue_scores, k, visualizer):
    """Block-Level Coloring and Scoring."""
    # print(f"BLOCK LEVEL COLORING AND SCORING")
    if block == 'G':
        return "blue", blue_scores['G']

    inherited_blue_set = set()  # Blue set inherited from the highest scoring parent
    additional_blue_set = set()  # To track additional parents added to the blue set for scoring purposes
    max_score_parent = None  # Parent with the highest blue score
    max_score = -1   # Initialize maximum score to a value that any valid score will exceed

    # print(f"Processing block: {block}")

    # Determine the parent with the maximum blue score
    for parent in dag.predecessors(block):
        parent_past = past(dag, parent)  # Retrieve past set of the parent
        if not parent_past:
            parent_past = {parent}  # If the parent past is empty, include the parent itself (Genesis)

        # print(f"Parent: {parent}, Parent Past: {parent_past}")

        # Include the parent itself in the inherited blue set
        current_inherited_set = parent_past.intersection(blue_set) | {parent}
        parent_score = blue_scores.get(parent, 0)  # Get the blue score of the parent

        if parent_score > max_score:
            max_score = parent_score
            max_score_parent = parent
            inherited_blue_set = current_inherited_set  # Update inherited blue set from the parent with the max score

    # print(f"Max Score Parent for block {block}: {max_score_parent} with score {max_score}")
    # print(f"Inherited Blue Set for block {block}: {inherited_blue_set}")

    # Recursive function to check and add to the blue set based on the K condition
    def check_and_add_to_blue_set(parent, inherited_blue_set):
        """Check and add to blue set used by the GhostForge research simulation."""
        blue_anticone = {b for b in anticone(dag, parent) if b in inherited_blue_set}  # Find blue anticone of the parent
        # print(f"Blue Anticone for parent {parent} of block {block}: {blue_anticone}")

        if len(blue_anticone) <= k:
            additional_blue_set.add(parent)  # Add parent to additional blue set if it meets K condition
            inherited_blue_set.add(parent)
            if parent in red_set:
                red_set.remove(parent)
                blue_set.add(parent)
            # print(f"Parent {parent} added to additional blue set for block {block}")
            # print(f"Extended blue set to check the anticones:  {inherited_blue_set}")

            # Check ancestors of the parent
            for ancestor in dag.predecessors(parent):
                if ancestor not in inherited_blue_set and ancestor not in additional_blue_set:
                    check_and_add_to_blue_set(ancestor, inherited_blue_set)
        else:
            red_set.add(parent)  # Add tip to red set if it doesn't meet K condition
            if parent in blue_set:
                blue_set.remove(parent)
            # print(f"Block {parent} added to Red Set (REC)")
            # Check ancestors of the tip
            for ancestor in dag.predecessors(parent):
                if ancestor not in inherited_blue_set and ancestor not in additional_blue_set:
                    check_and_add_to_blue_set(ancestor, inherited_blue_set)

    for parent in dag.predecessors(block):
        if parent != max_score_parent:
            check_and_add_to_blue_set(parent, inherited_blue_set)  # Check other parents

    # Check the block itself
    blue_anticone = {b for b in anticone(dag, block) if b in inherited_blue_set}
    # print(f"Final Blue Anticone for block {block}: {blue_anticone}")

    if len(blue_anticone) <= k:
        blue_set.add(block)  # Add block to blue set if it meets K condition
        block_score = len(inherited_blue_set) + 1  # Include the block itself in the score
        # print(f"Updated Score of {block}: {block_score}")
    else:
        block_score = len(inherited_blue_set)
        # print(f"Updated Score of {block}: {block_score}")

    # Update the scores of all affected blocks
    def update_block_scores(block, inherited_blue_set):
        """Update block scores used by the GhostForge research simulation."""
        for ancestor in inherited_blue_set:
            if ancestor in blue_set:
                blue_scores[ancestor] = len(past(dag, ancestor).intersection(blue_set)) + 1

    blue_scores[block] = block_score  # Set the blue score of the block
    update_block_scores(block, inherited_blue_set)  # Update scores of all blocks in the inherited blue set
    # print(f"Block {block} Score: {blue_scores[block]}")

    return "blue" if block in blue_set else "red", block_score


#Code started with 8/07/2024

def dag_level_coloring_and_ordering(dag, blue_set, red_set, blue_scores, k, previous_order, miner_id):
    """DAG-Level Coloring and Ordering."""
    # print(f"DAG LEVEL COLORING AND ORDERING")
    tips_list = list(tips(dag))  # Retrieve the tips of the DAG
    max_tip = max(tips_list, key=lambda x: blue_scores.get(x, 0))  # Select the tip with the maximum blue score
    # print(f"Selected Max Tip: {max_tip}")

    # Get blue set of max_tip (blocks that are blue and in the past of max_tip)
    blue_set_of_max_tip = {block for block in past(dag, max_tip) if block in blue_set}
    # print(f"Blue Set of Max Tip: {blue_set_of_max_tip}")

    # Add max_tip to its own blue set
    blue_set_of_max_tip.add(max_tip)
    # print(f"Updated Blue Set of Max Tip (including max_tip): {blue_set_of_max_tip}")

    # Perform the coloring
    inherited_blue_set = set(blue_set_of_max_tip)  # Blue set inherited from the max tip
    additional_blue_set = set(blue_set_of_max_tip)  # To track additional blue blocks added
    red_blocks_order = []  # List to maintain the order of blocks added to the red set
    # print(f"Inherited Blue Set: {inherited_blue_set}")
    # print(f"Initial Additional Blue Set: {additional_blue_set}")

    # Recursive function to check and add tips to the blue set based on the K condition
    def check_and_add_to_blue_set(tip, inherited_blue_set):
        """Check and add to blue set used by the GhostForge research simulation."""
        blue_anticone = {b for b in anticone(dag, tip) if b in inherited_blue_set}
        # print(f"Blue Anticone for tip {tip}: {blue_anticone}")

        if len(blue_anticone) <= k:
            inherited_blue_set.add(tip)  # Add tip to inherited blue set if it meets K condition
            additional_blue_set.add(tip)  # Track newly added blue blocks
            if tip in red_set:
                red_set.remove(tip)
                blue_set.add(tip)  # Remove from red set if it turns blue
            #     print(f"Block {tip} removed from Red Set")
            # print(f"Block {tip} added to additional blue set")
            # print(f"Extended blue set to check the anticones: {inherited_blue_set}")

            # Check ancestors of the tip
            for ancestor in dag.predecessors(tip):
                if ancestor not in inherited_blue_set and ancestor not in additional_blue_set:
                    check_and_add_to_blue_set(ancestor, inherited_blue_set)
        else:
            red_set.add(tip)  # Add tip to red set if it doesn't meet K condition
            red_blocks_order.append(tip)  # Keep track of the order in which blocks are added to the red set
            if tip in blue_set:
                blue_set.remove(tip)
            # print(f"Block {tip} added to Red Set (REC)")
            # Check ancestors of the tip
            for ancestor in dag.predecessors(tip):
                if ancestor not in inherited_blue_set and ancestor not in additional_blue_set:
                    check_and_add_to_blue_set(ancestor, inherited_blue_set)

    for tip in tips_list:
        if tip == max_tip:
            continue
        check_and_add_to_blue_set(tip, inherited_blue_set)  # Check other tips

    # Perform topological sort on the entire DAG starting with the max_tip
    topo_sorted_blocks = list(nx.topological_sort(dag))

    # Place max_tip at the beginning of the topological order
    if max_tip in topo_sorted_blocks:
        topo_sorted_blocks.remove(max_tip)
        topo_sorted_blocks.insert(0, max_tip)

    # Initialize the final order list and sets for tracking
    final_order = []
    seen_blocks = set()

    def add_block_in_order(block):
        """Add block in order used by the GhostForge research simulation."""
        if block not in seen_blocks:
            # Add all parents of the current block
            parents = list(dag.predecessors(block))
            # Sort parents by score (descending) and then alphabetically
            sorted_parents = sorted(parents, key=lambda x: (-blue_scores.get(x, 0), x))
            for parent in sorted_parents:
                add_block_in_order(parent)
            # Add the current block itself
            seen_blocks.add(block)
            final_order.append(block)

    # Start with the max_tip and process its ancestors
    add_block_in_order(max_tip)

    # Process the remaining tips
    remaining_tips = set(tips_list) - {max_tip}
    while remaining_tips:
        next_tip = max(remaining_tips, key=lambda x: blue_scores.get(x, 0))
        add_block_in_order(next_tip)
        remaining_tips.remove(next_tip)

    # Add red blocks to the end in the reverse order they were added to the red set
    # final_order.extend(red_blocks_order[::-1])  # Append red blocks in reverse order they were added

    print(f"Final Ordered List : {final_order} for MINER-ID {miner_id}") # (including red blocks at the end)

    return final_order, inherited_blue_set




def update_scores(dag, blue_set, red_set, blue_scores):
    """Update scores of all blocks in the DAG based on the current blue and red sets."""
    for block in nx.topological_sort(dag):
        if block == 'G':
            continue
        if block in blue_set:
            blue_score = len(past(dag, block).intersection(blue_set)) + 1  # Include the block itself in the score
        else:
            blue_score = len(past(dag, block).intersection(blue_set))
        blue_scores[block] = blue_score  # Set the blue score of the block

def apply_ghostforge(dag, new_blocks, blue_set, red_set, blue_scores, visualizer, previous_order, miner_id, k=3):
    """Apply the J_version protocol to new blocks in the DAG."""

    # Block-Level Coloring and Scoring
    for block in new_blocks:
        if block == 'G':
            continue
        color, score = block_level_coloring_and_scoring(dag, block, red_set,blue_set, blue_scores, k, visualizer)
        if color == "red":
            red_set.add(block)  # Add block to red set if its color is red

    # DAG-Level Coloring and Ordering
    ordered_list, max_blue_set = dag_level_coloring_and_ordering(dag, blue_set, red_set, blue_scores, k, previous_order, miner_id)

    return ordered_list, blue_set, red_set, blue_scores
