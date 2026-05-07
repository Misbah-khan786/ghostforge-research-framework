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
    print(f"BLOCK LEVEL COLORING AND SCORING")
    if block == 'G':
        return "blue", blue_scores['G']

    inherited_blue_set = set()  # Blue set inherited from the highest scoring parent
    additional_blue_set = set()  # To track additional parents added to the blue set for scoring purposes
    max_score_parent = None  # Parent with the highest blue score
    max_score = -1   # Initialize maximum score to a value that any valid score will exceed

    print(f"Processing block: {block}")

    # Determine the parent with the maximum blue score
    for parent in dag.predecessors(block):
        parent_past = past(dag, parent)  # Retrieve past set of the parent
        if not parent_past:
            parent_past = {parent}  # If the parent past is empty, include the parent itself (Genesis)

        print(f"Parent: {parent}, Parent Past: {parent_past}")

        # Include the parent itself in the inherited blue set
        current_inherited_set = parent_past.intersection(blue_set) | {parent}
        parent_score = blue_scores.get(parent, 0)  # Get the blue score of the parent

        if parent_score > max_score:
            max_score = parent_score
            max_score_parent = parent
            inherited_blue_set = current_inherited_set  # Update inherited blue set from the parent with the max score

    print(f"Max Score Parent for block {block}: {max_score_parent} with score {max_score}")
    print(f"Inherited Blue Set for block {block}: {inherited_blue_set}")

    # Recursive function to check and add to the blue set based on the K condition
    def check_and_add_to_blue_set(parent, inherited_blue_set):
        """Check and add to blue set used by the GhostForge research simulation."""
        blue_anticone = {b for b in anticone(dag, parent) if b in inherited_blue_set}  # Find blue anticone of the parent
        print(f"Blue Anticone for parent {parent} of block {block}: {blue_anticone}")

        if len(blue_anticone) <= k:
            additional_blue_set.add(parent)  # Add parent to additional blue set if it meets K condition
            inherited_blue_set.add(parent)
            if parent in red_set:
                red_set.remove(parent)
                blue_set.add(parent)
            print(f"Parent {parent} added to additional blue set for block {block}")
            print(f"Extended blue set to check the anticones:  {inherited_blue_set}")

            # Check ancestors of the parent
            for ancestor in dag.predecessors(parent):
                if ancestor not in inherited_blue_set and ancestor not in additional_blue_set:
                    check_and_add_to_blue_set(ancestor, inherited_blue_set)
        else:
            red_set.add(parent)  # Add tip to red set if it doesn't meet K condition
            if parent in blue_set:
                blue_set.remove(parent)
            print(f"Block {parent} added to Red Set (REC)")
            # Check ancestors of the tip
            for ancestor in dag.predecessors(parent):
                if ancestor not in inherited_blue_set and ancestor not in additional_blue_set:
                    check_and_add_to_blue_set(ancestor, inherited_blue_set)

    for parent in dag.predecessors(block):
        if parent != max_score_parent:
            check_and_add_to_blue_set(parent, inherited_blue_set)  # Check other parents

    # Check the block itself
    blue_anticone = {b for b in anticone(dag, block) if b in inherited_blue_set}
    print(f"Final Blue Anticone for block {block}: {blue_anticone}")

    if len(blue_anticone) <= k:
        blue_set.add(block)  # Add block to blue set if it meets K condition
        block_score = len(inherited_blue_set) + 1  # Include the block itself in the score
        print(f"Updated Score of {block}: {block_score}")
    else:
        block_score = len(inherited_blue_set)
        print(f"Updated Score of {block}: {block_score}")

    # Update the scores of all affected blocks
    def update_block_scores(block, inherited_blue_set):
        """Update block scores used by the GhostForge research simulation."""
        for ancestor in inherited_blue_set:
            if ancestor in blue_set:
                blue_scores[ancestor] = len(past(dag, ancestor).intersection(blue_set)) + 1

    blue_scores[block] = block_score  # Set the blue score of the block
    update_block_scores(block, inherited_blue_set)  # Update scores of all blocks in the inherited blue set
    print(f"Block {block} Score: {blue_scores[block]}")

    return "blue" if block in blue_set else "red", block_score

def dag_level_coloring_and_ordering(dag, blue_set, red_set, blue_scores, k, previous_order, miner_id):
    """DAG-Level Coloring and Ordering."""
    print(f"DAG LEVEL COLORING AND ORDERING")
    tips_list = list(tips(dag))  # Retrieve the tips of the DAG
    print(f"TIP LIST: {tips_list}")
    # Select the tip with the maximum blue score, with a tie-breaker on alphabetical order
    max_tip = max(tips_list, key=lambda x: (blue_scores.get(x, 0),-ord(x[0]))) # Select the tip with the maximum blue score
    print(f"Selected Max Tip: {max_tip}")

    # Get blue set of max_tip (blocks that are blue and in the past of max_tip)
    blue_set_of_max_tip = {block for block in past(dag, max_tip) if block in blue_set}
    print(f"Blue Set of Max Tip: {blue_set_of_max_tip}")

    # Add max_tip to its own blue set
    blue_set_of_max_tip.add(max_tip)
    print(f"Updated Blue Set of Max Tip (including max_tip): {blue_set_of_max_tip}")

    # Perform the coloring
    inherited_blue_set = set(blue_set_of_max_tip)  # Blue set inherited from the max tip
    additional_blue_set = set(blue_set_of_max_tip)  # To track additional blue blocks added
    red_blocks_order = []  # List to maintain the order of blocks added to the red set
    print(f"Inherited Blue Set: {inherited_blue_set}")
    print(f"Initial Additional Blue Set: {additional_blue_set}")

    # Recursive function to check and add tips to the blue set based on the K condition
    def check_and_add_to_blue_set(tip, inherited_blue_set):
        """Check and add to blue set used by the GhostForge research simulation."""
        blue_anticone = {b for b in anticone(dag, tip) if b in inherited_blue_set}
        print(f"Blue Anticone for tip {tip}: {blue_anticone}")

        if len(blue_anticone) <= k:
            inherited_blue_set.add(tip)  # Add tip to inherited blue set if it meets K condition
            additional_blue_set.add(tip)  # Track newly added blue blocks
            if tip in red_set:
                red_set.remove(tip)
                blue_set.add(tip)  # Remove from red set if it turns blue
                print(f"Block {tip} removed from Red Set")
            print(f"Block {tip} added to additional blue set")
            print(f"Extended blue set to check the anticones: {inherited_blue_set}")

            # Check ancestors of the tip
            for ancestor in dag.predecessors(tip):
                if ancestor not in inherited_blue_set and ancestor not in additional_blue_set:
                    check_and_add_to_blue_set(ancestor, inherited_blue_set)
        else:
            red_set.add(tip)  # Add tip to red set if it doesn't meet K condition
            red_blocks_order.append(tip)  # Keep track of the order in which blocks are added to the red set
            if tip in blue_set:
                blue_set.remove(tip)
            print(f"Block {tip} added to Red Set (REC)")
            # Check ancestors of the tip
            for ancestor in dag.predecessors(tip):
                if ancestor not in inherited_blue_set and ancestor not in additional_blue_set:
                    check_and_add_to_blue_set(ancestor, inherited_blue_set)

    for tip in tips_list:
        if tip == max_tip:
            continue
        check_and_add_to_blue_set(tip, inherited_blue_set)  # Check other tips

    new_order, inherited_blue_set = determine_new_order(
        dag, blue_set, red_set, blue_scores, k, previous_order, miner_id, max_tip, inherited_blue_set, red_blocks_order
    ,tips_list)

    return new_order, inherited_blue_set


def determine_new_order(dag, blue_set, red_set, blue_scores, k, previous_order, miner_id, max_tip,
                        inherited_blue_set, red_blocks_order, tips_list):
    """Determine the new order based on the DAG structure, blue scores, and inherited order."""

    print(f"STARTING THE ORDER for MINER-ID: {miner_id}")

    # Initialize the final order list and sets for tracking
    final_order = []
    seen_blocks = set()

    # Convert the previous_order to a set for quick lookup
    previous_order_set = set(previous_order)

    def find_max_parent_in_order(block):
        """Find the maximum parent in the previous order recursively."""
        parents = list(dag.predecessors(block))
        print(f"Finding parents for block {block}: {parents}")
        if not parents:
            return None
        # Sort parents by score (descending) and then alphabetically
        sorted_parents = sorted(parents, key=lambda x: (-blue_scores.get(x, 0), x))
        print(f"Sorted parents for block {block}: {sorted_parents}")
        for parent in sorted_parents:
            if parent in previous_order_set:
                print(f"Parent {parent} of block {block} is in the previous order")
                return parent
            max_parent = find_max_parent_in_order(parent)
            if max_parent:
                return max_parent
        return None

    def add_block_in_order(block):
        """Add block in order used by the GhostForge research simulation."""
        if block not in seen_blocks:
            # Add all parents of the current block
            parents = list(dag.predecessors(block))
            print(f"Adding block {block} with parents {parents}")
            # Sort parents by score (descending) and then alphabetically
            sorted_parents = sorted(parents, key=lambda x: (-blue_scores.get(x, 0), x))
            print(f"Sorted parents for block {block}: {sorted_parents}")
            for parent in sorted_parents:
                add_block_in_order(parent)
            # Add the current block itself
            seen_blocks.add(block)
            final_order.append(block)

            print(f"Added block {block}, current final order: {final_order}")

    # Find the max parent in order
    # max_parent = find_max_parent_in_order(max_tip)
    max_parent = max_tip if max_tip in previous_order_set else find_max_parent_in_order(max_tip)
    print(f"Selected Max Parent is {max_parent}")

    # Inherit order up to the max parent
    inherited_up_to = []
    if max_parent:
        for block in previous_order:
            if block not in seen_blocks:
                inherited_up_to.append(block)
                seen_blocks.add(block)
            if block == max_parent:
                break
        final_order.extend(inherited_up_to)
        print(f"Inherited order up to max parent {max_parent}: {final_order}")

    # Ensure max_tip and its ancestors are added in topological order
    add_block_in_order(max_tip)
    print(f"Added max_tip {max_tip}, current final order: {final_order}")

    # Process the remaining tips
    remaining_tips = set(tips_list) - {max_tip}
    print(f"Remaining tips to process: {remaining_tips}")
    while remaining_tips:
        next_tip = max(remaining_tips, key=lambda x: (blue_scores.get(x, 0), x))  # <-- Ensures tie-breaking alphabetically
        add_block_in_order(next_tip)
        remaining_tips.remove(next_tip)
        print(f"Processed tip {next_tip}, remaining tips: {remaining_tips}, current final order: {final_order}")

    # # Add red blocks to the end in the reverse order they were added to the red set
    # final_order.extend(red_blocks_order[::-1])  # Append red blocks in reverse order they were added

    print(f"Final Ordered List (including red blocks at the end): {final_order} for MINER-ID {miner_id}")

    return final_order, inherited_blue_set



# # Determine the inherited order
    # inherited_order = []
    # def find_inherited_order(block):
    #     nonlocal inherited_order
    #     if block in previous_order:
    #         inherited_order = previous_order[:previous_order.index(block) + 1]
    #         return True
    #     parents = list(dag.predecessors(block))
    #     if not parents:
    #         return False
    #     sorted_parents = sorted(parents, key=lambda x: (-blue_scores.get(x, 0), x))
    #     for parent in sorted_parents:
    #         if find_inherited_order(parent):
    #             return True
    #     return False
    #
    # if not find_inherited_order(max_tip):
    #     inherited_order = []
    #
    # print(f"Inherited Order: {inherited_order}")
    #
    # # Ensure inherited_order is a list
    # if isinstance(inherited_order, str):
    #     inherited_order = [inherited_order]
    # elif not isinstance(inherited_order, list):
    #     inherited_order = list(inherited_order)
    #
    # # Remove red blocks from the inherited order
    # inherited_order = [block for block in inherited_order if block]
    # print(f"Inherited Order (excluding red blocks): {inherited_order}")
    #
    # # Start with the blocks in the past of max_tip but not part of the inherited order
    # past_blocks = set(past(dag, max_tip))
    # additional_order_set = past_blocks - set(inherited_order)
    #
    # # Function to recursively add blocks in topological order based on scores and alphabetical order
    # def add_block_in_order(block, order_set):
    #     if block not in order_set:
    #         parents = list(dag.predecessors(block))
    #         sorted_parents = sorted(parents, key=lambda x: (-blue_scores.get(x, 0), x))
    #         for parent in sorted_parents:
    #             add_block_in_order(parent, order_set)
    #         order_set.add(block)
    #
    # # Start with the max_tip and process its ancestors
    # add_block_in_order(max_tip, additional_order_set)
    # additional_order = [block for block in additional_order_set if block not in inherited_order]
    #
    # # Add max_tip if not already in new_order
    # if max_tip not in additional_order:
    #     additional_order.append(max_tip)
    #
    # # Construct the new order
    # new_order = []
    # added_blocks = set()
    #
    # # Add inherited order to the new order
    # for block in inherited_order:
    #     if block not in added_blocks:
    #         new_order.append(block)
    #         added_blocks.add(block)
    #
    # # Add additional blue blocks
    # for block in additional_order:
    #     if block not in added_blocks:
    #         new_order.append(block)
    #         added_blocks.add(block)
    #
    # print(f"New Order after Adding Blue Blocks (excluding red blocks): {new_order}")
    #
    # # Determine remaining tips not in new_order
    # remaining_tips = [tip for tip in tips_list if tip not in new_order]
    # remaining_tips_sorted = sorted(remaining_tips, key=lambda x: (-blue_scores.get(x, 0), x))
    # for tip in remaining_tips_sorted:
    #     if tip not in added_blocks:
    #         new_order.append(tip)
    #         added_blocks.add(tip)
    #
    # print(f"New Order after Adding Remaining Tips: {new_order}")
    #
    # # Append red blocks at the end in the reverse order they were added
    # red_blocks_sorted = red_blocks_order[::-1]
    # for block in red_blocks_sorted:
    #     if block not in added_blocks:
    #         new_order.append(block)
    #         added_blocks.add(block)
    #
    # print(f"Final Ordered List (including red blocks at the end): {new_order} for MINER-ID {miner_id}")
    #
    # return new_order, inherited_blue_set

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
