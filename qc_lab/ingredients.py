"""
This file contains ingredient functions for use in Model classes.
"""

import functools
import numpy as np
from numba import njit


def z_to_qp(z, constants):
    """
    Convert complex coordinates to real coordinates.
    """
    h = constants.classical_coordinate_weight
    m = constants.classical_coordinate_mass
    q = np.real((1 / np.sqrt(2 * m * h)) * (z + np.conj(z)))
    p = np.real(1.0j * np.sqrt((m * h) / 2) * (np.conj(z) - z))
    return q, p


def qp_to_z(q, p, constants):
    """
    Convert real coordinates to complex coordinates.
    """
    h = constants.classical_coordinate_weight
    m = constants.classical_coordinate_mass
    z = np.sqrt((m * h) / 2) * q + 1.0j * np.sqrt(1 / (2 * m * h)) * p
    return z


def make_ingredient_sparse(ingredient):
    """
    Wrapper that converts a vectorized ingredient output to a sparse format
    consisting of the indices (inds), nonzero elements (mels), and shape.
    """

    @functools.wraps(ingredient)
    def sparse_ingredient(*args, **kwargs):
        (model, constants, parameters) = args
        out = ingredient(model, constants, parameters, **kwargs)
        inds = np.where(out != 0)
        mels = out[inds]
        shape = np.shape(out)
        return inds, mels, shape

    return sparse_ingredient


def vectorize_ingredient(ingredient):
    """
    Wrapper that vectorize an ingredient function.
    It assumes that any kwarg is an numpy.ndarray is vectorized over its first index.
    Other kwargs are assumed to not be vectorized.
    """

    @functools.wraps(ingredient)
    def vectorized_ingredient(*args, **kwargs):
        (model, constants, parameters) = args
        if kwargs.get("batch_size") is not None:
            batch_size = kwargs.get("batch_size")
        else:
            batch_size = len(parameters.seed)
        keys = kwargs.keys()
        kwargs_list = []
        for n in range(batch_size):
            kwargs_n = {}
            for key in keys:
                if isinstance(kwargs[key], np.ndarray):
                    kwargs_n[key] = kwargs[key][n]
                else:
                    kwargs_n[key] = kwargs[key]
            kwargs_list.append(kwargs_n)
        out = np.array(
            [
                ingredient(model, constants, parameters, **kwargs_list[n])
                for n in range(batch_size)
            ]
        )
        return out

    return vectorized_ingredient


def harmonic_oscillator_h_c(model, parameters, **kwargs):
    """
    Harmonic oscillator classical Hamiltonian function.

    Required Constants:
        - `harmonic_oscillator_frequency`: Array of harmonic oscillator frequencies.
    """
    del parameters
    z = kwargs.get("z")
    if kwargs.get("batch_size") is not None:
        batch_size = kwargs.get("batch_size")
        assert len(z) == batch_size
    else:
        batch_size = len(z)
    w = model.constants.harmonic_oscillator_frequency[np.newaxis, :]
    m = model.constants.classical_coordinate_mass[np.newaxis, :]
    q, p = z_to_qp(z, model.constants)
    h_c = np.sum((1 / 2) * (((p**2) / m) + m * (w**2) * (q**2)), axis=-1)
    return h_c


@njit()
def harmonic_oscillator_dh_c_dzc_jit(z, h, w):
    """
    Numba accelerated calculation of the gradient of the Harmonic oscillator Hamiltonian.
    """
    a = (1 / 2) * (((w**2) / h) - h)
    b = (1 / 2) * (((w**2) / h) + h)
    out = b[..., :] * z + a[..., :] * np.conj(z)
    return out


def harmonic_oscillator_dh_c_dzc(model, parameters, **kwargs):
    """
    Derivative of the classical harmonic oscillator Hamiltonian with respect to the `z` coordinate.

    Required Constants:
        - `harmonic_oscillator_frequency`: Array of harmonic oscillator frequencies.
    """
    del parameters
    z = kwargs.get("z")
    if kwargs.get("batch_size") is not None:
        batch_size = kwargs.get("batch_size")
        assert len(z) == batch_size
    else:
        batch_size = len(z)
    h = model.constants.classical_coordinate_weight
    w = model.constants.harmonic_oscillator_frequency
    return harmonic_oscillator_dh_c_dzc_jit(z, h, w)


def two_level_system_h_q(model, parameters, **kwargs):
    """
    Quantum Hamiltonian for a two-level system.

    Required Constants:
        - `two_level_system_a`: Energy of the first level.
        - `two_level_system_b`: Energy of the second level.
        - `two_level_system_c`: Real part of the coupling between levels.
        - `two_level_system_d`: Imaginary part of the coupling between levels.
    """
    if kwargs.get("batch_size") is not None:
        batch_size = kwargs.get("batch_size")
    else:
        batch_size = len(parameters.seed)
    h_q = np.zeros((batch_size, 2, 2), dtype=complex)
    h_q[:, 0, 0] = model.constants.two_level_system_a
    h_q[:, 1, 1] = model.constants.two_level_system_b
    h_q[:, 0, 1] = (
        model.constants.two_level_system_c + 1j * model.constants.two_level_system_d
    )
    h_q[:, 1, 0] = (
        model.constants.two_level_system_c - 1j * model.constants.two_level_system_d
    )
    return h_q


@njit
def nearest_neighbor_lattice_h_q_jit(
    batch_size, num_sites, hopping_energy, periodic_boundary
):
    """
    Low level function to generate the nearest-neighbor lattice quantum Hamiltonian.
    """
    out = np.zeros((batch_size, num_sites, num_sites)) + 0.0j
    for b in range(batch_size):
        for n in range(num_sites - 1):
            out[b, n, n + 1] = -hopping_energy + 0.0j
            out[b, n + 1, n] = -np.conj(hopping_energy) + 0.0j
        if periodic_boundary:
            out[b, 0, num_sites - 1] = -hopping_energy + 0.0j
            out[b, num_sites - 1, 0] = -np.conj(hopping_energy) + 0.0j
    return out


def nearest_neighbor_lattice_h_q(model, parameters, **kwargs):
    """
    Quantum Hamiltonian for a nearest-neighbor lattice.

    Required Constants:
        - `nearest_neighbor_lattice_hopping_energy`: Hopping energy between sites.
        - `nearest_neighbor_lattice_periodic_boundary`: Boolean indicating periodic boundary conditions.
    """
    if kwargs.get("batch_size") is not None:
        batch_size = kwargs.get("batch_size")
    else:
        batch_size = len(parameters.seed)
    num_sites = model.constants.num_quantum_states
    hopping_energy = model.constants.nearest_neighbor_lattice_hopping_energy
    periodic_boundary = model.constants.nearest_neighbor_lattice_periodic_boundary
    if hasattr(model, "h_q_mat"):
        if model.h_q_mat is not None:
            if len(model.h_q_mat) == batch_size:
                return model.h_q_mat
    h_q = np.zeros((num_sites, num_sites), dtype=complex)
    # Fill the Hamiltonian matrix with hopping energies.
    for n in range(num_sites - 1):
        h_q[n, n + 1] += -hopping_energy
        h_q[n + 1, n] += np.conj(h_q[n, n + 1])
    # Apply periodic boundary conditions if specified.
    if periodic_boundary:
        h_q[0, num_sites - 1] += -hopping_energy
        h_q[num_sites - 1, 0] += np.conj(h_q[0, num_sites - 1])
    model.h_q_mat = h_q[np.newaxis, :, :] + np.zeros(
        (batch_size, num_sites, num_sites), dtype=complex
    )
    return model.h_q_mat


@njit()
def diagonal_linear_h_qc_jit(
    batch_size, num_sites, num_classical_coordinates, z, gamma
):
    """
    Low level function to generate the diagonal linear quantum-classical coupling Hamiltonian.
    """
    h_qc = np.zeros((batch_size, num_sites, num_sites)) + 0.0j
    for b in range(batch_size):
        for i in range(num_sites):
            for j in range(num_classical_coordinates):
                h_qc[b, i, i] = h_qc[b, i, i] + gamma[i, j] * (
                    z[b, j] + np.conj(z[b, j])
                )
    return h_qc


def diagonal_linear_h_qc(model, parameters, **kwargs):
    """
    Diagonal linear quantum-classical coupling Hamiltonian.

    Diagonal elements are given by

    :math:`H_{ii} = \sum_{j} \gamma_{ij} (z_{j} + z_{j}^*)`

    Required Constants:
        - `diagonal_linear_coupling`: Array of coupling constants (num_quantum_states, num_classical_coordinates).
    """
    del parameters
    z = kwargs["z"]
    if kwargs.get("batch_size") is not None:
        batch_size = kwargs.get("batch_size")
        assert len(z) == batch_size
    else:
        batch_size = len(z)
    num_sites = model.constants.num_quantum_states
    num_classical_coordinates = model.constants.num_classical_coordinates
    gamma = model.constants.diagonal_linear_coupling
    return diagonal_linear_h_qc_jit(
        batch_size, num_sites, num_classical_coordinates, z, gamma
    )


def diagonal_linear_dh_qc_dzc(model, parameters, **kwargs):
    """
    Gradient of the diagonal linear quantum-classical coupling Hamiltonian.

    Required Constants:
        - `diagonal_linear_coupling`: Array of coupling constants (num_quantum_states, num_classical_coordinates).
    """
    z = kwargs["z"]
    if kwargs.get("batch_size") is not None:
        batch_size = kwargs.get("batch_size")
    else:
        batch_size = len(parameters.seed)
    recalculate = False
    if model.dh_qc_dzc_shape is not None:
        if model.dh_qc_dzc_shape[0] != batch_size:
            recalculate = True
    if (
        model.dh_qc_dzc_inds is None
        or model.dh_qc_dzc_mels is None
        or model.dh_qc_dzc_shape is None
        or recalculate
    ):

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
        model.dh_qc_dzc_inds = inds
        model.dh_qc_dzc_mels = dh_qc_dzc[inds]
        model.dh_qc_dzc_shape = shape
        return inds, mels, shape
    return model.dh_qc_dzc_inds, model.dh_qc_dzc_mels, model.dh_qc_dzc_shape


def harmonic_oscillator_hop_function(model, parameters, **kwargs):
    """
    Perform a hopping operation for the harmonic oscillator.

    Required Constants:
        - `harmonic_oscillator_frequency`: Array of harmonic oscillator frequencies.
    """
    del parameters
    z = kwargs["z"]
    delta_z = kwargs["delta_z"]
    ev_diff = kwargs["ev_diff"]
    hopped = False
    delta_zc = np.conj(delta_z)
    zc = np.conj(z)
    a_const = (1 / 4) * (
        (
            (model.constants.harmonic_oscillator_frequency**2)
            / model.constants.classical_coordinate_weight
        )
        - model.constants.classical_coordinate_weight
    )
    b_const = (1 / 4) * (
        (
            (model.constants.harmonic_oscillator_frequency**2)
            / model.constants.classical_coordinate_weight
        )
        + model.constants.classical_coordinate_weight
    )
    akj_z = np.sum(
        2 * delta_zc * delta_z * b_const - a_const * (delta_z**2 + delta_zc**2)
    )
    bkj_z = 2j * np.sum(
        (z * delta_z - delta_zc * zc) * a_const
        + (delta_z * zc - delta_zc * z) * b_const
    )
    ckj_z = ev_diff
    disc = bkj_z**2 - 4 * akj_z * ckj_z
    if disc >= 0:
        if bkj_z < 0:
            gamma = bkj_z + np.sqrt(disc)
        else:
            gamma = bkj_z - np.sqrt(disc)
        if akj_z == 0:
            gamma = 0
        else:
            gamma = gamma / (2 * akj_z)
        # adjust classical coordinate
        z = z - 1.0j * np.real(gamma) * delta_z
        hopped = True
    return z, hopped


def harmonic_oscillator_boltzmann_init_classical(model, parameters, **kwargs):
    """
    Initialize classical coordinates according to Boltzmann statistics for the harmonic oscillator.

    Required Constants:
        - `kBT`: Thermal quantum.
        - `harmonic_oscillator_frequency`: Array of harmonic oscillator frequencies.
    """
    del parameters
    seed = kwargs.get("seed", None)
    kBT = model.constants.kBT
    w = model.constants.harmonic_oscillator_frequency
    m = model.constants.classical_coordinate_mass
    out = np.zeros(
        (len(seed), model.constants.num_classical_coordinates), dtype=complex
    )
    for s, seed_value in enumerate(seed):
        np.random.seed(seed_value)
        # Calculate the standard deviations for q and p.
        std_q = np.sqrt(kBT / (m * (w**2)))
        std_p = np.sqrt(m * kBT)
        # Generate random q and p values.
        q = np.random.normal(
            loc=0, scale=std_q, size=model.constants.num_classical_coordinates
        )
        p = np.random.normal(
            loc=0, scale=std_p, size=model.constants.num_classical_coordinates
        )
        # Calculate the complex-valued classical coordinate.
        z = qp_to_z(q, p, model.constants)
        out[s] = z
    return out


def harmonic_oscillator_wigner_init_classical(model, parameters, **kwargs):
    """
    Initialize classical coordinates according to the Wigner distribution of the ground state of a harmonic oscillator.

    Required Constants:
        - `kBT`: Thermal quantum.
        - `harmonic_oscillator_frequency`: Array of harmonic oscillator frequencies.
    """
    del parameters
    seed = kwargs.get("seed", None)
    m = model.constants.classical_coordinate_mass
    w = model.constants.harmonic_oscillator_frequency
    kBT = model.constants.kBT
    out = np.zeros(
        (len(seed), model.constants.num_classical_coordinates), dtype=complex
    )
    for s, seed_value in enumerate(seed):
        np.random.seed(seed_value)

        # Calculate the standard deviations for q and p.
        if kBT > 0:
            std_q = np.sqrt(1 / (2 * w * m * np.tanh(w / (2 * (kBT)))))
            std_p = np.sqrt((m * w) / (2 * np.tanh(w / (2 * (kBT)))))
        else:
            std_q = np.sqrt(1 / (2 * w * m))
            std_p = np.sqrt((m * w) / (2))
        # Generate random q and p values.
        q = np.random.normal(
            loc=0, scale=std_q, size=model.constants.num_classical_coordinates
        )
        p = np.random.normal(
            loc=0, scale=std_p, size=model.constants.num_classical_coordinates
        )
        # Calculate the complex-valued classical coordinate.
        z = qp_to_z(q, p, model.constants)
        out[s] = z
    return out


def harmonic_oscillator_coherent_state_wigner_init_classical(
    model, parameters, **kwargs
):
    """
    Initialize classical coordinates according to the Wigner distribution of a coherent state of a harmonic oscillator.

    exp(a * b^{\dagger} - a^* * b)

    where `a` is the complex displacement parameter of the coherent state.

    Required Constants:
        - `coherent_state_displacement`: Array of complex displacement parameter for the coherent state.
        - `harmonic_oscillator_frequency`: Array of harmonic oscillator frequencies.
    """
    del parameters
    seed = kwargs.get("seed", None)
    a = model.constants.coherent_state_displacement
    m = model.constants.classical_coordinate_mass
    w = model.constants.harmonic_oscillator_frequency
    out = np.zeros(
        (len(seed), model.constants.num_classical_coordinates), dtype=complex
    )
    for s, seed_value in enumerate(seed):
        np.random.seed(seed_value)
        # Calculate the standard deviations for q and p.
        std_q = np.sqrt(1 / (2 * w * m))
        std_p = np.sqrt((m * w) / (2))
        mu_q = np.sqrt(2 / (m * w)) * np.real(a)
        mu_p = np.sqrt(2 / (m * w)) * np.imag(a)
        # Generate random q and p values.
        q = np.random.normal(
            loc=mu_q, scale=std_q, size=model.constants.num_classical_coordinates
        )
        p = np.random.normal(
            loc=mu_p, scale=std_p, size=model.constants.num_classical_coordinates
        )
        # Calculate the complex-valued classical coordinate.
        z = qp_to_z(q, p, model.constants)
        out[s] = z
    return out
