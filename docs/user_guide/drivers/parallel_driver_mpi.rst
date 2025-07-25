.. _parallel_driver_mpi:




MPI Driver
~~~~~~~~~~

The `parallel_driver_mpi` function in the `qc_lab.dynamics` module is used to run simulations 
in parallel using the `mpi4py` library. This driver is suitable for use in cluster environments 
and is compatible with different schedulers like SLURM. Unlike the multiprocessing driver, the MPI driver
requires a script to be run using the `mpiexec` or `mpirun` command.

.. note::

    This driver introduces some complexity due to compatibilities and the need for MPI to be set up correctly. For that reason, 
    we exclude `mpi4py` from the default installation of QC Lab. To install it and use this driver, you can run:
    
    .. code-block:: bash

        pip install mpi4py



Function Signature
------------------

.. code-block:: python

    qc_lab.dynamics.parallel_driver_mpi(sim, seeds=None, data=None, num_tasks=None)

Parameters
----------

- **sim** (*Simulation*): The simulation object that contains the model, settings, and state.
- **seeds** (*array-like, optional*): An array of seed values for the random number generator. If not provided, seeds will be generated automatically.
- **data** (*Data, optional*): A Data object to store the results of the simulation. If not provided, a new Data object will be created.
- **num_tasks** (*int, optional*): The number of parallel tasks (processes) to use for the simulation. If not provided, the number of available MPI processes will be used.

Returns
-------

- **data** (*Data*): A Data object containing the results of the simulation.

Example
-------

Here is an example of how to use the `parallel_driver_mpi` function to run a simulation in parallel. Suppose the 
following code is saved in a script called `mpi_example.py`and that the simulation object has been set up 
according to the quickstart guide.:

.. code-block:: python

    # Import the parallel driver
    from qc_lab.dynamics import parallel_driver_mpi
    # Import the MPI module
    from mpi4py import MPI

    # Initialize the sim object using the quickstart guide

    # Run the simulation using the parallel driver
    data = parallel_driver_mpi(sim, num_tasks=100)

    # Determine the rank of the current process
    rank = MPI.COMM_WORLD.Get_rank()
    if rank = 0:
        # do something with the data only on the master process
        print(data)


The parallel execution can be started using the `mpiexec` or `mpirun` command where the number of tasks
used in the execution should be the same as the one used in the call to `parallel_driver_mpi`. For example:

.. code-block:: bash

    mpirun -n 100 python parallel_example.py


If using a scheduler like SLURM, the number of tasks can be specified in the job script. For example:

.. code-block:: bash

    #!/bin/bash
    #SBATCH -A # your allocation
    #SBATCH -p # your partition
    #SBATCH -N 2
    #SBATCH --ntasks-per-node 50
    #SBATCH --cpus-per-task 1
    #SBATCH -t 01:00:00
    #SBATCH --mem-per-cpu=1G

    ulimit -c 0
    ulimit -s unlimited

    mpirun -n 100 python mpi_example.py


Notes
-----

- This driver is suitable for use in cluster environments and is compatible with different schedulers like SLURM.
- For single-node calculations, optionally consider using the multiprocessing driver.

References
----------

- `mpi4py library <https://mpi4py.readthedocs.io/en/stable/>`_