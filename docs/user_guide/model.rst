.. _model:

==========================
Models
==========================

Models in QC Lab define the physics of the quantum-classical system under study. A model object is an instance of the ``qclab.Model`` class and is equipped with a set of constants and ingredients that specify the properties of the system in a manner that is agnostic to the quantum-classical algorithm being used.

At a minimum, the model object defines the Hamiltonian of the system:

.. math::

    H(q,p) = \hat{H}_{\mathrm{q}} + \hat{H}_{\mathrm{q-c}}(q) + H_{\mathrm{c}}(q,p)

where :math:`\hat{H}_\mathrm{q}` is the quantum Hamiltonian, :math:`\hat{H}_{\mathrm{q-c}}(q)` is the quantum-classical coupling Hamiltonian, and :math:`H_{\mathrm{c}}(q,p)` is the classical Hamiltonian. These ingredients are discussed in detail in 
:ref:`Ingredients <ingredient>`.


The model object also contains a mandatory set of constants that define properties of the system:

- ``num_quantum_states``: the number of quantum states in the system,
- ``num_classical_coordinates``: the number of classical coordinates in the system,
- ``classical_coordinate_mass``: the mass of the classical coordinates,
- ``classical_coordinate_weight``: the weight of the classical coordinates (:math:`h` in the complex-coordinate formalism).


The Model Class
--------------------------

The model class is defined in the ``qclab.Model`` module. It is equipped with a constants object ``model.constants``, an ingredients list ``model.ingredients``, and a dictionary of default constants ``model.default_constants``.


Constants
~~~~~~~~~~~~~~~~~~~~~~~~~~

Often, a model's properties can be captured by a set of high-level constants that are suitable for user input. For example, the spin-boson model is defined by the following user-defined constants:

- ``kBT``: the thermal energy at a given temperature,
- ``l_reorg``: the reorganization energy of the bath,
- ``E``: the energy bias between the two quantum states,
- ``V``: the diabatic coupling between the two quantum states,
- ``A``: the number of bosonic modes in the bath,
- ``W``: the characteristic frequency of the bosonic modes in the bath.
- ``boson_mass``: the mass of each bosonic mode in the bath.

Each of these constants have a default value stored in the dictionary ``model.default_constants``. At initialization, these defaults can be overwritten by passing a dictionary to the model constructor, as in:

.. code-block:: python

    from qclab.models import SpinBoson

    # Create a dictionary of input constants to overwrite the defaults.
    input_constants = {
        "kBT": 1.0,
        "l_reorg": 0.005,
        "E": 0.5,
        "V": 0.5,
        "A": 100,
        "W": 0.1,
        "boson_mass": 1.0
    }
    # Initialize the spin-boson model with the input constants.
    model = SpinBoson(input_constants)

These input constants are first read into the model's constants object ``model.constants`` which is an instance of the ``qclab.Constants`` class. Any input constants that are not specified will take on their default values. The input constants are then used to compute the mandatory constants required by QC Lab (specified above), as well as any additional constants that may be needed by the ingredients of the model. This computation is performed by a set of initialization ingredients that are typically unique to each model. The resulting "internal" constants are stored in the model's constants object.

For example, the spin-boson model class uses the following initialization ingredients to compute its constants:

.. note::

    When included within a class, the first argument of the ingredient is ``self`` instead of ``model``. Here, specifying them outside of the class, we use ``model`` to refer to the instance of the model class.

.. code-block:: python

    def _init_h_q(model, parameters, **kwargs):
        """
        Initializes the constants required for the two-level quantum Hamiltonian.
        """
        model.constants.two_level_00 = model.constants.get("E")
        model.constants.two_level_11 = -model.constants.get("E")
        model.constants.two_level_01_re = model.constants.get("V")
        model.constants.two_level_01_im = 0
        return

    def _init_h_qc(model, parameters, **kwargs):
        """
        Initializes the constants required for the diagonal linear quantum-classical Hamiltonian.
        """
        A = model.constants.get("A")
        l_reorg = model.constants.get("l_reorg")
        boson_mass = model.constants.get("boson_mass")
        h = model.constants.classical_coordinate_weight
        w = model.constants.harmonic_frequency
        model.constants.diagonal_linear_coupling = np.zeros((2, A))
        model.constants.diagonal_linear_coupling[0] = (
            w * np.sqrt(2.0 * l_reorg / A) * (1.0 / np.sqrt(2.0 * boson_mass * h))
        )
        model.constants.diagonal_linear_coupling[1] = (
            -w * np.sqrt(2.0 * l_reorg / A) * (1.0 / np.sqrt(2.0 * boson_mass * h))
        )
        return

    def _init_h_c(model, parameters, **kwargs):
        """
        Initializes the constants required for the harmonic classical Hamiltonian.
        """
        A = model.constants.get("A")
        W = model.constants.get("W")
        model.constants.harmonic_frequency = W * np.tan(
            np.arange(0.5, A + 0.5, 1.0) * np.pi * 0.5 / A
        )
        return

    def _init_model(model, parameters, **kwargs):
        """
        Initializes the mandatory constants required by QC Lab.
        """
        A = model.constants.get("A")
        boson_mass = model.constants.get("boson_mass")
        model.constants.num_classical_coordinates = A
        model.constants.num_quantum_states = 2
        model.constants.classical_coordinate_weight = model.constants.harmonic_frequency
        model.constants.classical_coordinate_mass = boson_mass * np.ones(A)
        return


For more information on the formatting of an ingredient, please refer to :ref:`Ingredients <ingredient>`. In the subsequent section we will discuss how these ingredients are included in a model class.


Ingredients List
~~~~~~~~~~~~~~~~~~~~~~~~~~

The ingredients in a model are contained in a list of tuples ``model.ingredients``. Each tuple contains the name of the ingredient as a string and the ingredient function itself. For example, the spin-boson model includes the following ingredients:


.. code-block:: python

    ingredients = [
        ("h_q", ingredients.h_q_two_level),
        ("h_qc", ingredients.h_qc_diagonal_linear),
        ("h_c", ingredients.h_c_harmonic),
        ("dh_qc_dzc", ingredients.dh_qc_dzc_diagonal_linear),
        ("dh_c_dzc", ingredients.dh_c_dzc_harmonic),
        ("init_classical", ingredients.init_classical_boltzmann_harmonic),
        ("hop", ingredients.hop_harmonic),
        ("_init_h_q", _init_h_q),
        ("_init_h_qc", _init_h_qc),
        ("_init_model", _init_model),
        ("_init_h_c", _init_h_c),
    ]


As you can see, the ingredients list includes both the Hamiltonian ingredients (``h_q``, ``h_qc``, ``h_c``), their gradients (``dh_qc_dzc``, ``dh_c_dzc``), as well as other ingredients used in the dynamics (``init_classical``, ``hop``). Other ingredients define initialization steps that compute the model's constants (``_init_h_q``, ``_init_h_qc``, ``_init_h_c``, ``_init_model``). These are distinguished by their leading underscore, which indicates that they are to be run when the model is initialized. 

To initialize the model's constants manually one can run 

.. code-block:: python

    model.initialize_constants()

which will execute all the ingredients in the list that begin with an underscore. After doing so, all the internal constants will be available in the model's constants object ``model.constants``. By default, this is done whenever a model object is initialized and whenever a constant is changed.


Importantly, a model's ingredients list is executed from back to front. This means that one can add or overwrite an existing ingredient by appending a new tuple to the ingredients list. For example, if we wanted to change the quantum-classical coupling from diagonal to off-diagonal coupling, we could define a new ingredient and append it to the ingredients list:

.. code-block:: python

    from qclab import ingredients

    def h_qc_off_diagonal(model, parameters, **kwargs):
        """
        A vectorized ingredient that couples the boson coordinates 
        to the off-diagonal elements of the quantum Hamiltonian.
        """
        z = kwargs['z']
        A = model.constants.get("A")
        m = model.constants.classical_coordinate_mass
        h = model.constants.classical_coordinate_weight
        g = model.constants.diagonal_linear_coupling[0]
        N = model.constants.num_quantum_states
        batch_size = len(z)
        h_qc = np.zeros((batch_size, N, N), dtype=complex)
        h_qc[:, 0, 1] = g[np.newaxis, :] * (z + np.conj(z))
        h_qc[:, 1, 0] = np.conj(h_qc[:, 0, 1])
        return h_qc

    # Overwrite the quantum-classical coupling ingredient.
    model.ingredients.append(("h_qc", h_qc_off_diagonal))
    # Overwrite the gradient of the quantum-classical coupling ingredient.
    model.ingredients.append(("dh_qc_dzc", None))  # No analytical gradient available.


.. _spinboson_model:
Spin-Boson Model
--------------------------

.. list-table:: Spin-Boson Model Constants
   :header-rows: 1
   :widths: 25 50 25

   * - Constant
     - Description
     - Default
   * - ``kBT``
     - Thermal energy.
     - 1.0
   * - ``V``
     - Onsite energy.
     - 0.5
   * - ``E``
     - Diabatic coupling.
     - 0.5
   * - ``A``
     - Number of bosonic modes.
     - 100
   * - ``W``
     - Characteristic frequency.
     - 0.1
   * - ``l_reorg``
     - Reorganization energy.
     - 0.005
   * - ``boson_mass``
     - Boson mass.
     - 1.0


.. dropdown:: View full source
   :icon: code

   .. literalinclude:: ../../src/qclab/models/spin_boson.py
      :language: python
      :linenos:

FMO Complex Model
--------------------------

.. list-table:: FMO Model Constants
   :header-rows: 1
   :widths: 25 50 25

   * - Constant
     - Description
     - Default
   * - ``kBT``
     - Thermal energy.
     - 1
   * - ``mass``
     - Coordinate mass.
     - 1
   * - ``l_reorg``
     - Reorganization energy.
     - 35 cm :sup:`-1`
   * - ``w_c``
     - Characteristic frequency.
     - 106.14 cm :sup:`-1`
   * - ``N``
     - Number of bosonic modes.
     - 200


.. dropdown:: View full source
   :icon: code

   .. literalinclude:: ../../src/qclab/models/fmo_complex.py
      :language: python
      :linenos:


Tully Problem One
--------------------------

.. list-table:: Tully Problem One Model Constants
   :header-rows: 1
   :widths: 25 50 25

   * - Constant
     - Description
     - Default
   * - ``init_momentum``
     - Initial momentum.
     - 10.0
   * - ``init_position``
     - Initial position.
     - -25.0
   * - ``mass``
     - Coordinate mass.
     - 2000.0
   * - ``A``
     - See reference publication.
     - 0.01
   * - ``B``
     - See reference publication.
     - 1.6
   * - ``C``
     - See reference publication.
     - 0.005
   * - ``D``
     - See reference publication.
     - 1.0

.. dropdown:: View full source
   :icon: code

   .. literalinclude:: ../../src/qclab/models/tully_problem_one.py
      :language: python
      :linenos:


