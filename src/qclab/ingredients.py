"""
This module contains ingredients for use in Model classes.
"""

import numpy as np
from qclab import functions


def h_c_harmonic(model, parameters, **kwargs):
    """
    Harmonic oscillator classical Hamiltonian function.

    :math:`H_{\mathrm{c}} = \\frac{1}{2}\\sum_{n} \\left( \\frac{p_n^2}{m_n} + m_n \\omega_n^2 q_n^2 \\right)`

    .. rubric:: Keyword Args
    z : ndarray
        Complex classical coordinate.

    .. rubric:: Model Constants
    harmonic_frequency : ndarray
        Harmonic frequency of each classical coordinate.

    .. rubric:: Returns
    h_c : ndarray
        Classical Hamiltonian.
        ``(batch_size,)``.
    """
    z = kwargs["z"]
    w = model.constants.harmonic_frequency[np.newaxis, :]
    m = model.constants.classical_coordinate_mass[np.newaxis, :]
    h = model.constants.classical_coordinate_weight[np.newaxis, :]
    q = functions.z_to_q(z, m, h)
    p = functions.z_to_p(z, m, h)
    h_c = np.sum(0.5 * (((p**2) / m) + m * (w**2) * (q**2)), axis=-1)
    return h_c


def h_c_free(model, parameters, **kwargs):
    """
    Free particle classical Hamiltonian function.

    :math:`H_{\mathrm{c}} = \\sum_{n} \\left( \\frac{p_n^2}{2m_n} \\right)`

    .. rubric:: Keyword Args
    z : ndarray
        Complex classical coordinate.

    .. rubric:: Model Constants
    None

    .. rubric:: Returns
    h_c : ndarray
        Classical Hamiltonian.
        ``(batch_size,)``.
    """
    z = kwargs["z"]
    m = model.constants.classical_coordinate_mass[np.newaxis, :]
    h = model.constants.classical_coordinate_weight[np.newaxis, :]
    p = functions.z_to_p(z, m, h)
    h_c = np.sum((0.5 / m) * (p**2), axis=-1)
    return h_c


def dh_c_dzc_harmonic(model, parameters, **kwargs):
    """
    Derivative of the harmonic oscillator classical Hamiltonian function with respect to
    the conjugate z coordinate. This is an ingredient that calls the low-level
    function ``dh_c_dzc_harmonic_jit``.

    .. rubric:: Keyword Args
    z : ndarray
        Complex classical coordinate.

    .. rubric:: Model Constants
    harmonic_frequency : ndarray
        Harmonic frequency of each classical coordinate.

    .. rubric:: Returns
    dh_c_dzc : ndarray
        Gradient of the classical Hamiltonian with respect to the conjugate classical
        coordinate.
        ``(batch_size, num_classical_coordinates)``.
    """
    z = kwargs["z"]
    h = model.constants.classical_coordinate_weight
    w = model.constants.harmonic_frequency
    return functions.dh_c_dzc_harmonic_jit(z, h, w)


def dh_c_dzc_free(model, parameters, **kwargs):
    """
    Derivative of the free particle classical Hamiltonian function with respect to the
    conjugate z coordinate.

    .. rubric:: Keyword Args
    z : ndarray
        Complex classical coordinate.

    .. rubric:: Model Constants
    None

    .. rubric:: Returns
    dh_c_dzc : ndarray
        Gradient of the classical Hamiltonian with respect to the conjugate classical
        coordinate.
        ``(batch_size, num_classical_coordinates)``.
    """
    z = kwargs["z"]
    h = model.constants.classical_coordinate_weight[np.newaxis, :]
    return 1j * h * z.imag


def h_q_two_level(model, parameters, **kwargs):
    """
    Quantum Hamiltonian for a two-level system.

    :math:`H_{nm} = \\delta_{nm}\\mathrm{two\\_level\\_nn}+(1-\\delta_{nm})(\\mathrm{two\\_level\\_nm\\_re} + i \\mathrm{two\\_level\\_nm\\_im})`

    .. rubric:: Keyword Args
    batch_size : int
        Number of trajectories in a batch.

    .. rubric:: Model Constants
    two_level_00 : float
        Energy of the first level.
    two_level_11 : float
        Energy of the second level.
    two_level_01_re : float
        Real part of the off-diagonal coupling.
    two_level_01_im : float
        Imaginary part of the off-diagonal coupling.

    .. rubric:: Returns
    h_q : ndarray
        Quantum Hamiltonian.
        ``(batch_size, num_states, num_states)``.
    """
    batch_size = kwargs["batch_size"]
    h_q = np.zeros((2, 2), dtype=complex)
    h_q[0, 0] = model.constants.get("two_level_00", 0.0)
    h_q[1, 1] = model.constants.get("two_level_11", 0.0)
    h_q[0, 1] = model.constants.get("two_level_01_re", 0.0) + 1j * model.constants.get(
        "two_level_01_im", 0.0
    )
    h_q[1, 0] = model.constants.get("two_level_01_re", 0.0) - 1j * model.constants.get(
        "two_level_01_im", 0.0
    )
    # We use np.broadcast_to because each trajectory is identical.
    return np.broadcast_to(h_q, (batch_size, 2, 2))


def h_q_nearest_neighbor(model, parameters, **kwargs):
    """
    Quantum Hamiltonian for a nearest-neighbor lattice.

    :math:`H_{nm} = -t (\\delta_{n,m+1} + \\delta_{n,m-1})`

    .. rubric:: Keyword Args
    batch_size : int
        Number of trajectories in a batch.

    .. rubric:: Model Constants
    nearest_neighbor_hopping_energy : float
        Hopping energy between sites :math:`t`.
    nearest_neighbor_periodic : bool
        Whether to apply periodic boundary conditions.

    .. rubric:: Returns
    h_q : ndarray
        Quantum Hamiltonian.
        ``(batch_size, num_states, num_states)``.
    """
    batch_size = kwargs["batch_size"]
    num_sites = model.constants.num_quantum_states
    hopping_energy = model.constants.nearest_neighbor_hopping_energy
    periodic = model.constants.nearest_neighbor_periodic
    h_q = np.zeros((num_sites, num_sites), dtype=complex)
    # Fill the Hamiltonian matrix with hopping energies.
    for n in range(num_sites - 1):
        h_q[n, n + 1] = -hopping_energy
        h_q[n + 1, n] = np.conj(h_q[n, n + 1])
    # Apply periodic boundary conditions if specified.
    # Note that for num_sites = 2 the off-diagonal is
    # hopping_energy, not 2*hopping_energy.
    if periodic:
        h_q[0, num_sites - 1] = -hopping_energy
        h_q[num_sites - 1, 0] = np.conj(h_q[0, num_sites - 1])
    # We use np.broadcast_to because each trajectory is identical.
    return np.broadcast_to(h_q, (batch_size, num_sites, num_sites))


def h_qc_diagonal_linear(model, parameters, **kwargs):
    """
    Diagonal linear quantum-classical Hamiltonian.

    :math:`H_{nm} = \\delta_{nm}\\sum_{j} \\gamma_{nj} (z_{j} + z_{j}^*)`

    .. rubric:: Keyword Args
    z : ndarray
        Complex classical coordinate.

    .. rubric:: Model Constants
    diagonal_linear_coupling : ndarray
        Coupling constants :math:`\\gamma`.

    .. rubric:: Returns
    h_qc : ndarray
        Quantum-classical coupling Hamiltonian.
        ``(batch_size, num_states, num_states)``.
    """
    z = kwargs["z"]
    gamma = model.constants.diagonal_linear_coupling
    return functions.h_qc_diagonal_linear_jit(z, gamma)


def dh_qc_dzc_diagonal_linear(model, parameters, **kwargs):
    """
    Gradient of the diagonal linear quantum-classical coupling Hamiltonian
    in sparse format.

    :math:`[\\partial_{z} H_{qc}]_{ijkl} = \\delta_{kl}\\gamma_{kj}`

    .. rubric:: Keyword Args
    z : ndarray
        Complex classical coordinate.

    .. rubric:: Model Constants
    diagonal_linear_coupling : ndarray
        Coupling constants :math:`\\gamma`.

    .. rubric:: Returns
    inds : tuple of ndarray
        Indices of the non-zero elements of the gradient.
        ``(batch_index, coordinate_index, row_index, column_index)``.
    mels : ndarray
        Values of the non-zero elements of the gradient.
    shape : tuple
        Shape of the full gradient array.
        ``(batch_size, num_classical_coordinates, num_states, num_states)``.
    """
    z = kwargs["z"]
    batch_size = len(z)
    num_states = model.constants.num_quantum_states
    num_classical_coordinates = model.constants.num_classical_coordinates
    gamma = model.constants.diagonal_linear_coupling
    dh_qc_dzc = np.zeros(
        (num_classical_coordinates, num_states, num_states), dtype=complex
    )
    for i in range(num_states):
        for j in range(num_classical_coordinates):
            dh_qc_dzc[j, i, i] = gamma[i, j]
    dh_qc_dzc = dh_qc_dzc[np.newaxis, :, :, :] + np.zeros(
        (batch_size, num_classical_coordinates, num_states, num_states),
        dtype=complex,
    )
    inds = np.where(dh_qc_dzc != 0)
    mels = dh_qc_dzc[inds]
    shape = np.shape(dh_qc_dzc)
    return inds, mels, shape


def hop_harmonic(model, parameters, **kwargs):
    """
    FSSH hop function for taking the classical coordinates to represent harmonic
    oscillators.

    Determines the shift in the classical coordinates required to conserve energy
    following a hop between quantum states.

    If enough energy is available, the function returns the shift in the classical
    coordinates such that the new classical coordinate is ``z + shift`` and a Boolean
    equaling ``True`` if the hop has occurred. If not enough energy is available,
    the shift becomes zero and the Boolean is ``False``.

    Solves the equation:

    .. math::

        H_{\mathrm{c}}(z) + \epsilon_{\mathrm{initial}} = H_{\mathrm{c}}(z + \mathrm{shift}) +
        \epsilon_{\mathrm{final}}

    .. rubric:: Keyword Args
    z : ndarray
        Current classical coordinate.
    resc_dir_z : ndarray
        Rescaling direction of ``z``.
    eigval_diff : float
        Energy difference between final and initial states.

    .. rubric:: Model Constants
    harmonic_frequency : ndarray
        Harmonic frequency of each classical coordinate.

    .. rubric:: Returns
    shift : ndarray
        Shift in the classical coordinate.
    hop : bool
        Whether the hop has occurred.
    """
    z = kwargs["z"]
    resc_dir_z = kwargs["resc_dir_z"]
    eigval_diff = kwargs["eigval_diff"]
    w = model.constants.harmonic_frequency
    h = model.constants.classical_coordinate_weight
    resc_dir_zc = np.conj(resc_dir_z)
    a_const = 0.25 * (((w**2) / h) - h)
    b_const = 0.25 * (((w**2) / h) + h)
    # Here, akj_z, bkj_z, ckj_z are the coefficients of the quadratic equation
    # akj_z * gamma^2 - bkj_z * gamma + ckj_z = 0
    akj_z = np.sum(
        2.0 * resc_dir_zc * resc_dir_z * b_const
        - a_const * (resc_dir_z**2 + resc_dir_zc**2)
    )
    bkj_z = 2.0 * np.sum(
        h * z.imag * resc_dir_z.real - (w**2 / h) * z.real * resc_dir_z.imag
    )
    ckj_z = eigval_diff
    disc = bkj_z**2 - 4.0 * akj_z * ckj_z
    if disc >= 0:
        if bkj_z < 0:
            gamma = bkj_z + np.sqrt(disc)
        else:
            gamma = bkj_z - np.sqrt(disc)
        if akj_z == 0:
            gamma = 0
        else:
            gamma = 0.5 * gamma / akj_z
        shift = -1j * gamma * resc_dir_z
        return shift, True
    shift = np.zeros_like(z)
    return shift, False


def hop_free(model, parameters, **kwargs):
    """
    FSSH hop function taking the classical coordinates to represent free particles.

    Determines the shift in the classical coordinates required to conserve energy
    following a hop between quantum states.

    If enough energy is available, the function returns the shift in the classical
    coordinates such that the new classical coordinate is ``z + shift`` and a Boolean
    equaling ``True`` if the hop has occurred. If not enough energy is available,
    the shift becomes zero and the Boolean is ``False``.

    Solves the equation:

    .. math::

        H_{\mathrm{c}}(z) + \epsilon_{\mathrm{initial}} = H_{\mathrm{c}}(z + \mathrm{shift}) +
        \epsilon_{\mathrm{final}}

    .. rubric:: Keyword Args
    z : ndarray
        Current classical coordinate.
    resc_dir_z : ndarray
        Rescaling direction.
    eigval_diff : float
        Energy difference between final and initial states.

    .. rubric:: Model Constants
    None

    .. rubric:: Returns
    shift : ndarray
        Shift in the classical coordinate.
    hop : bool
        Whether the hop has occurred.
    """
    z = kwargs["z"]
    resc_dir_z = kwargs["resc_dir_z"]
    eigval_diff = kwargs["eigval_diff"]
    h = model.constants.classical_coordinate_weight
    # Here, akj_z, bkj_z, ckj_z are the coefficients of the quadratic equation
    # akj_z * gamma^2 - bkj_z * gamma + ckj_z = 0
    f = 1j * 2.0 * resc_dir_z.real
    g = -2.0j * z.imag
    akj_z = np.sum(0.25 * h * f * f)
    bkj_z = -np.sum(0.5 * h * f * g)
    ckj_z = -eigval_diff
    disc = bkj_z**2 - 4.0 * akj_z * ckj_z
    if disc >= 0:
        if bkj_z < 0:
            gamma = bkj_z + np.sqrt(disc)
        else:
            gamma = bkj_z - np.sqrt(disc)
        if akj_z == 0:
            gamma = 0
        else:
            gamma = 0.5 * gamma / akj_z
        shift = -1j * gamma * resc_dir_z
        return shift, True
    shift = np.zeros_like(z)
    return shift, False


def init_classical_boltzmann_harmonic(model, parameters, **kwargs):
    """
    Initialize classical coordinates according to Boltzmann statistics taking the
    classical coordinates to represent harmonic oscillators.


    :math:`P(z) \\propto \\exp(-H_{\mathrm{c}}/k_{\mathrm{B}}T)`

    .. rubric:: Keyword Args
    seed : ndarray, int
        Random seeds for each trajectory.

    .. rubric:: Model Constants
    kBT : float
        Thermal quantum.
    harmonic_frequency : ndarray
        Harmonic frequency of each classical coordinate.

    .. rubric:: Returns
    z : ndarray
        Complex classical coordinate.
    """
    seed = kwargs["seed"]
    kBT = model.constants.kBT
    w = model.constants.harmonic_frequency
    m = model.constants.classical_coordinate_mass
    h = model.constants.classical_coordinate_weight
    out = np.ascontiguousarray(
        np.zeros((len(seed), model.constants.num_classical_coordinates), dtype=complex)
    )
    # Calculate the standard deviations for q and p.
    std_q = np.sqrt(kBT / (m * (w**2)))
    std_p = np.sqrt(m * kBT)
    for s, seed_value in enumerate(seed):
        np.random.seed(seed_value)
        # Generate random q and p values.
        q = np.random.normal(
            loc=0, scale=std_q, size=model.constants.num_classical_coordinates
        )
        p = np.random.normal(
            loc=0, scale=std_p, size=model.constants.num_classical_coordinates
        )
        # Calculate the complex-valued classical coordinate.
        out[s] = functions.qp_to_z(q, p, m, h)
    return out


def init_classical_wigner_harmonic(model, parameters, **kwargs):
    """
    Initialize classical coordinates according to the Wigner distribution of the ground
    state of a harmonic oscillator.

    .. rubric:: Keyword Args
    seed : ndarray, int
        Random seeds for each trajectory.

    .. rubric:: Model Constants
    kBT : float
        Thermal quantum.
    harmonic_frequency : ndarray
        Harmonic frequency of each classical coordinate.

    .. rubric:: Returns
    z : ndarray
        Complex classical coordinate.
    """
    seed = kwargs["seed"]
    w = model.constants.harmonic_frequency
    m = model.constants.classical_coordinate_mass
    h = model.constants.classical_coordinate_weight
    kBT = model.constants.kBT
    out = np.zeros(
        (len(seed), model.constants.num_classical_coordinates), dtype=complex
    )
    # Calculate the standard deviations for q and p.
    if kBT > 0:
        std_q = np.sqrt(0.5 / (w * m * np.tanh(0.5 * w / kBT)))
        std_p = np.sqrt(0.5 * m * w / np.tanh(0.5 * w / kBT))
    else:
        std_q = np.sqrt(0.5 / (w * m))
        std_p = np.sqrt(0.5 * m * w)
    for s, seed_value in enumerate(seed):
        np.random.seed(seed_value)
        # Generate random q and p values.
        q = np.random.normal(
            loc=0, scale=std_q, size=model.constants.num_classical_coordinates
        )
        p = np.random.normal(
            loc=0, scale=std_p, size=model.constants.num_classical_coordinates
        )
        # Calculate the complex-valued classical coordinate.
        out[s] = functions.qp_to_z(q, p, m, h)
    return out


def init_classical_definite_position_momentum(model, parameters, **kwargs):
    """
    Initialize classical coordinates with definite position and momentum.

    .. rubric:: Keyword Args
    seed : ndarray, int
        Random seeds for each trajectory.

    .. rubric:: Model Constants
    init_position : ndarray
        Initial position of the classical coordinates.
    init_momentum : ndarray
        Initial momentum of the classical coordinates.

    .. rubric:: Returns
    z : ndarray
        Complex classical coordinate.
    """
    seed = kwargs["seed"]
    q = model.constants.init_position
    p = model.constants.init_momentum
    m = model.constants.classical_coordinate_mass
    h = model.constants.classical_coordinate_weight
    z = np.zeros((len(seed), model.constants.num_classical_coordinates), dtype=complex)
    for s, seed_value in enumerate(seed):
        np.random.seed(seed_value)
        z[s] = functions.qp_to_z(q, p, m, h)
    return z


def init_classical_wigner_coherent_state(model, parameters, **kwargs):
    """
    Initialize classical coordinates according to the Wigner distribution of a coherent
    state of a harmonic oscillator.

    :math:`\\vert a\\rangle = \\exp(a\\hat{b}^{\\dagger} - a^{*}\\hat{b})\\vert 0\\rangle`

    where :math:`a` is the complex displacement parameter of the coherent state. The Wigner
    distribution is given by

    :math:`P(z) \\propto \\exp(-2\\vert(z - a)\\vert^{2})`.

    .. rubric:: Keyword Args
    seed : ndarray, int
        Random seeds for each trajectory.

    .. rubric:: Model Constants
    coherent_state_displacement : ndarray
        Complex displacement parameter of the coherent state.
    harmonic_frequency : ndarray
        Harmonic frequency of each classical coordinate.

    .. rubric:: Returns
    z : ndarray
        Complex classical coordinate.
    """
    seed = kwargs["seed"]
    a = model.constants.coherent_state_displacement
    w = model.constants.harmonic_frequency
    m = model.constants.classical_coordinate_mass
    h = model.constants.classical_coordinate_weight
    out = np.zeros(
        (len(seed), model.constants.num_classical_coordinates), dtype=complex
    )
    # Calculate the standard deviations for q and p.
    std_q = np.sqrt(0.5 / (w * m))
    std_p = np.sqrt(0.5 * m * w)
    mu_q = np.sqrt(2.0 / (m * w)) * np.real(a)
    mu_p = np.sqrt(2.0 * m * w) * np.imag(a)
    for s, seed_value in enumerate(seed):
        np.random.seed(seed_value)
        # Generate random q and p values.
        q = np.random.normal(
            loc=mu_q, scale=std_q, size=model.constants.num_classical_coordinates
        )
        p = np.random.normal(
            loc=mu_p, scale=std_p, size=model.constants.num_classical_coordinates
        )
        # Calculate the z coordinate.
        z = functions.qp_to_z(q, p, m, h)
        out[s] = z
    return out


def rescaling_direction_random(model, parameters, **kwargs):
    """
    Random rescaling direction function.

    This function returns a random array for the rescaling direction.
    It is only included for documentation purposes.

    Note that this is not a vectorized ingredient, as it is only called on
    the per-trajectory level.

    .. rubric:: Keyword Args
    z_traj : ndarray
        Current classical coordinate in the trajectory being rescaled.
    init_state_ind : int
        Index of the initial quantum state.
    final_state_ind : int
        Index of the final quantum state.

    .. rubric:: Model Constants
    None

    .. rubric:: Returns
    resc_dir_z : ndarray
        Direction in which to rescale coordinates.
    """
    z_traj = kwargs["z_traj"]
    init_state_ind = kwargs["init_state_ind"]
    final_state_ind = kwargs["final_state_ind"]
    return np.random.normal(size=z_traj.shape)


def gauge_field_force_zero(model, parameters, **kwargs):
    """
    Gauge field force function.

    This function returns a zero array for the gauge field force.
    It is only included for documentation purposes.

    .. rubric:: Keyword Args
    z : ndarray
        Current classical coordinate.
    state_ind : int
        Index of the state for which the gauge field force is calculated.


    .. rubric:: Model Constants
    None

    .. rubric:: Returns
    gauge_force : ndarray
        Gauge field force.
    """
    z = kwargs["z"]
    state_ind = kwargs["state_ind"]
    return np.zeros_like(z)
