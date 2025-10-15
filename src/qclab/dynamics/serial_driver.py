"""
This module contains the serial driver.
"""

import logging
import numpy as np
import qclab.dynamics as dynamics
from qclab.utils import get_log_output, reset_log_output
from qclab import Data

logger = logging.getLogger(__name__)


def serial_driver(sim, seeds=None, data=None):
    """
    Serial driver for the dynamics core.

    .. rubric:: Args
    sim: Simulation
        The simulation object containing the model, algorithm, initial state, and settings.
    seeds: ndarray, optional
        An array of integer seeds for the trajectories. If None, seeds will be
        generated automatically.
    data: Data, optional
        A Data object for collecting output data. If None, a new Data object
        will be created.

    .. rubric:: Returns
    data: Data
        The updated Data object containing collected output data.
    """
    # Clear any in-memory log output from previous runs.
    reset_log_output()
    # First initialize the model constants.
    sim.model.initialize_constants()
    if data is None:
        data = Data()
    if seeds is None:
        if len(data.data_dict["seed"]) > 0:
            offset = np.max(data.data_dict["seed"]) + 1
        else:
            offset = 0
        seeds = offset + np.arange(sim.settings.num_trajs, dtype=int)
        num_trajs = sim.settings.num_trajs
    else:
        num_trajs = len(seeds)
        logger.warning(
            "Setting sim.settings.num_trajs to the number of provided seeds: %s",
            num_trajs,
        )
        sim.settings.num_trajs = num_trajs
    # Determine the number of batches required to execute the total number
    # of trajectories.
    if num_trajs % sim.settings.batch_size == 0:
        num_batches = num_trajs // sim.settings.batch_size
    else:
        num_batches = int(num_trajs / sim.settings.batch_size) + 1

    logger.info(
        "Running %s batches with %s seeds in each batch.",
        num_batches,
        sim.settings.batch_size,
    )
    for n in range(num_batches):
        batch_seeds = seeds[
            n * sim.settings.batch_size : (n + 1) * sim.settings.batch_size
        ]
        if len(batch_seeds) == 0:
            break
        logger.info("Running batch %s with seeds %s.", n + 1, batch_seeds)
        sim.settings.batch_size = len(batch_seeds)
        sim.initialize_timesteps()
        parameters = {}
        state = {"seed": batch_seeds}
        new_data = Data(batch_seeds)
        logger.info("Starting dynamics calculation.")
        new_data = dynamics.run_dynamics(sim, state, parameters, new_data)
        logger.info("Dynamics calculation completed.")
        logger.info("Collecting results.")
        data.add_data(new_data)
    logger.info("Simulation complete.")
    # Attach the collected log output to the data object before returning.
    data.log = get_log_output()
    return data
