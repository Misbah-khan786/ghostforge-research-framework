# GhostForge Research Simulation Framework

This repository contains Python research code developed during my PhD to simulate and evaluate DAG-based distributed ledger consensus mechanisms, including GhostForge variants.

The code is intended as a research prototype rather than production software. It demonstrates how DAG structures, miner/node behaviour, propagation delays, block colouring, scoring, and ordering rules can be modelled and analysed under different network conditions.

## Research Context

GhostForge investigates scalable consensus for DAG-based distributed ledgers. The broader research objective is to understand how large-scale distributed systems behave under dynamic conditions such as concurrent block creation, network delay, and changing local views of the DAG.

This type of simulation work is relevant to complex infrastructure modelling more broadly, where system-level behaviour emerges from interactions between many distributed components.

## Repository Structure

```text
GhostForge/
├── DAG/              # DAG helper functions: past set, anticone, tips, score helpers
├── GHOSTFORGE/       # Consensus, colouring, scoring, ordering, and tip-selection logic
├── Network/          # Miner/node models and propagation-delay support
├── DAGVisulizer/     # Visualisation utilities for DAG states and protocol behaviour
├── dynamic.py        # Example simulation runner
├── requirements.txt  # Python dependencies
└── README.md
```

## Main Capabilities

- DAG construction and traversal
- Miner/node-level simulation
- Propagation-delay modelling
- Block colouring and scoring
- Tip selection and ordering variants
- Visualisation of DAG states
- Experimentation with different protocol behaviours

## Requirements

Install dependencies with:

```bash
pip install -r requirements.txt
```

Typical dependencies include:

- `networkx`
- `matplotlib`
- `numpy`
- `pandas`
- `graphviz` / `pygraphviz` where visualisation is required

## Example Usage

Run the example simulation driver:

```bash
python dynamic.py
```

Some scripts may require minor configuration of simulation parameters such as number of miners, propagation delay, block generation rate, or protocol variant.

## Key Experimental Features

### THR (Threaded Simulation)
Support for threaded simulation experiments where miner and network activities can execute concurrently. This was used to analyse protocol behaviour under parallel block generation and propagation conditions.

### DY (Dynamic Block Generation)
Dynamic DAG growth simulation where block generation rates and miner behaviour evolve during runtime. This supports modelling adaptive network conditions and varying system loads.

### Manual Miner and Block Entry
Support for controlled experimental configurations with manually specified miners, blocks, and DAG structures for deterministic evaluation and debugging.

### Network Delay Modelling
Simulation of distributed propagation delays between miners/nodes to analyse the effect of latency on consensus convergence and DAG growth.

### Block Scoring and Ordering
Experimental implementations of score-based ordering, coloring, and GhostForge ordering mechanisms.

### CLM Extensions
Support for Coloring Locking Mechanism (CLM) experiments, including locked coloring regions and stability-oriented ordering behaviour.

## System Assumptions

The simulation framework models distributed DAG-based consensus systems under the following assumptions:

- **λ (Lambda):** Block generation rate controlling DAG growth and miner activity.
- **α (Alpha):** Fraction of adversarial hashing/mining power used in security experiments.
- **D:** Network propagation delay between distributed miners/nodes.
- **K:** Anticone threshold used for coloring and blue/red set determination.
- **N:** Number of participating miners/nodes in the simulation.

## Research Progression

This repository represents the progression of multiple research works developed during my PhD research:

1. Early DAG network and distributed simulation experiments
2. GHOSTForge consensus mechanism
3. Optimized block ordering experiments
4. Coloring Locking Mechanism (CLM) extensions

The framework evolved incrementally to support experimentation on DAG growth, miner coordination, scoring, ordering, coloring, and stability analysis.
## Related Publications

1. GHOSTForge: A Scalable Consensus Mechanism for DAG-Based Blockchains  
IEEE Open Journal of the Computer Society, 2024

2. Optimized Block Ordering in DAG-Based Distributed Ledgers  
IEEE Open Journal of the Computer Society, 2025

3. Coloring Locking Mechanism (CLM) for DAG Consensus  
Submitted to IEEE Transactions on Information Forensics and Security
## Notes for Reviewers

This repository is provided as a compact research-code sample. Generated output files, virtual environments, IDE files, and large experimental artefacts have been removed to keep the repository focused on the core implementation.

## Related Research

This code is associated with research on DAG-based distributed ledger consensus, including GhostForge and related simulation-based evaluation work.

## Disclaimer

This repository is a research simulation framework developed for experimental evaluation and academic research purposes. The implementation is intended for simulation and analysis rather than production deployment.
