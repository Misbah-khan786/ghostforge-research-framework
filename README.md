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

## Notes for Reviewers

This repository is provided as a compact research-code sample. Generated output files, virtual environments, IDE files, and large experimental artefacts have been removed to keep the repository focused on the core implementation.

## Related Research

This code is associated with research on DAG-based distributed ledger consensus, including GhostForge and related simulation-based evaluation work.
