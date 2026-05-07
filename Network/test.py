"""Network and miner models used to simulate distributed block creation and propagation.

These classes coordinate miner behaviour, propagation delays, and interactions between local miner views of the DAG."""

def dag_level_coloring_and_ordering(dag, blue_set, red_set, blue_scores, k, previous_order, miner_id):
    """DAG-Level Coloring and Ordering."""
    print(f"DAG LEVEL COLORING AND ORDERING")
    tips_list = list(tips(dag))  # Retrieve the tips of the DAG
    max_tip = max(tips_list, key=lambda x: blue_scores.get(x, 0))  # Select the tip with the maximum blue score
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

    # Determine the inherited order
    if max_tip in previous_order:
        inherited_order = previous_order[:previous_order.index(max_tip) + 1]
    else:
        max_parent = max(dag.predecessors(max_tip), key=lambda x: blue_scores.get(x, 0), default=None)
        if max_parent and max_parent in previous_order:
            inherited_order = previous_order[:previous_order.index(max_parent) + 1]
        else:
            inherited_order = []

    print(f"Inherited Order: {inherited_order}")

    # Ensure inherited_order is a list
    if isinstance(inherited_order, str):
        inherited_order = [inherited_order]
    elif not isinstance(inherited_order, list):
        inherited_order = list(inherited_order)

    # Remove red blocks from the inherited order
    inherited_order = [block for block in inherited_order if block not in red_set]
    print(f"Inherited Order (excluding red blocks): {inherited_order}")

    # Determine additional blue blocks
    new_blue_blocks = [block for block in additional_blue_set if block not in inherited_order and block not in red_set]
    print(f"New Blue Blocks to Add: {new_blue_blocks}")

    # Convert the topological sort generator to a list
    topo_sorted_blocks = list(nx.topological_sort(dag))

    # Sort new blue blocks by topological order and their scores
    new_blue_blocks_sorted = sorted(new_blue_blocks, key=lambda x: (topo_sorted_blocks.index(x), blue_scores.get(x, 0)))
    print(f"New Blue Blocks Sorted by Score: {new_blue_blocks_sorted}")

    # Construct the new order
    new_order = inherited_order + new_blue_blocks_sorted
    print(f"New Order after Adding Blue Blocks (excluding red blocks): {new_order}")

    # Append red blocks at the end, sorted by their scores in descending order
    red_blocks_sorted = sorted(red_set, key=lambda x: blue_scores.get(x, 0), reverse=False)
    print(f"Red Blocks Sorted by Score: {red_blocks_sorted}")

    new_order += red_blocks_sorted
    print(f"Final Ordered List (including red blocks at the end): {new_order}")

    return new_order, inherited_blue_set


# second best
def dag_level_coloring_and_ordering(dag, blue_set, red_set, blue_scores, k, previous_order, miner_id):
    """DAG-Level Coloring and Ordering."""
    print(f"DAG LEVEL COLORING AND ORDERING")
    tips_list = list(tips(dag))  # Retrieve the tips of the DAG
    max_tip = max(tips_list, key=lambda x: blue_scores.get(x, 0))  # Select the tip with the maximum blue score
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

    # Determine the inherited order
    if max_tip in previous_order:
        inherited_order = previous_order[:previous_order.index(max_tip) + 1]
    else:
        max_parent = max(dag.predecessors(max_tip), key=lambda x: blue_scores.get(x, 0), default=None)
        if max_parent and max_parent in previous_order:
            inherited_order = previous_order[:previous_order.index(max_parent) + 1]
        else:
            inherited_order = []

    print(f"Inherited Order: {inherited_order}")

    # Ensure inherited_order is a list
    if isinstance(inherited_order, str):
        inherited_order = [inherited_order]
    elif not isinstance(inherited_order, list):
        inherited_order = list(inherited_order)

    # Remove red blocks from the inherited order
    inherited_order = [block for block in inherited_order if block not in red_set]
    print(f"Inherited Order (excluding red blocks): {inherited_order}")

    # Determine additional blue blocks that are in the past of max_tip but not in inherited_order
    past_blocks = set(past(dag, max_tip))
    additional_blue_blocks_of_max_tip = [block for block in additional_blue_set if block in past_blocks and block not in inherited_order and block not in red_set]
    print(f"Additional Blue Blocks to Add: {additional_blue_blocks_of_max_tip}")

    # Perform topological sort on the subgraph of blocks in the past of max_tip
    subgraph = dag.subgraph(past_blocks.union({max_tip}))
    topo_sorted_blocks = list(nx.topological_sort(subgraph))

    # Sort additional blue blocks by topological order and their scores
    additional_blue_blocks_sorted = sorted(additional_blue_blocks_of_max_tip, key=lambda x: (topo_sorted_blocks.index(x), blue_scores.get(x, 0)))
    print(f"Additional Blue Blocks Sorted by Score: {additional_blue_blocks_sorted}")

    # Add max_tip if not already in new_order
    if max_tip not in additional_blue_blocks_sorted:
        additional_blue_blocks_sorted.append(max_tip)

        # Construct the new order
        new_order = inherited_order + additional_blue_blocks_sorted
        print(f"New Order after Adding Blue Blocks (excluding red blocks): {new_order}")

        # Determine remaining tips not in new_order
        remaining_tips = [tip for tip in tips_list if tip not in new_order]
        remaining_tips_subgraph = dag.subgraph(remaining_tips)
        remaining_tips_sorted = sorted(remaining_tips, key=lambda x: (
        list(nx.topological_sort(remaining_tips_subgraph)).index(x), blue_scores.get(x, 0)), reverse=True)
        new_order += remaining_tips_sorted
        print(f"New Order after Adding Remaining Tips: {new_order}")

        # Append red blocks at the end, sorted by their scores in descending order
        red_blocks_sorted = sorted(red_set, key=lambda x: blue_scores.get(x, 0), reverse=False)
        print(f"Red Blocks Sorted by Score: {red_blocks_sorted}")

        new_order += red_blocks_sorted
        print(f"Final Ordered List (including red blocks at the end): {new_order} for MINER-ID {miner_id}")

        return new_order, inherited_blue_set
