"""Network and miner models used to simulate distributed block creation and propagation.

These classes coordinate miner behaviour, propagation delays, and interactions between local miner views of the DAG."""

import random
class MinerDelayMatrix:
    """Encapsulate related simulation state and behaviour for the MinerDelayMatrix component."""
    def __init__(self, delay_data=None):
        # List of miners to generate random delays for
        """  init   used by the GhostForge research simulation."""
        miners = ['M1', 'M2', 'M3', 'M4', 'Master']
        # Initialize with random delays between 15ms to 30ms if none are provided
        if delay_data is None:
            delay_data = {}
            for miner_from in miners:
                delay_data[miner_from] = {}
                for miner_to in miners:
                    if miner_from != miner_to:
                        delay_data[miner_from][miner_to] = random.randint(15, 30)
        self.delay_data = delay_data

    def get_delay(self, miner_id_from, miner_id_to):
        """Get delay used by the GhostForge research simulation."""
        return self.delay_data.get(miner_id_from, {}).get(miner_id_to, 1000)