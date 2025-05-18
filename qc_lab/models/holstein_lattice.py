"""
This file contains the Holstein lattice Model class.
"""

import numpy as np
from qc_lab.model import Model
from qc_lab import ingredients


class HolsteinLattice(Model):
    """
    A model representing a nearest-neighbor tight-binding model
    with Holstein-type electron-phonon coupling with a
    single optical mode.
    """

    def __init__(self, constants=None):
        if constants is None:
            constants = {}
        self.default_constants = {
            "kBT": 1,
            "g": 0.5,
            "w": 0.5,
            "N": 10,
            "J": 1,
            "phonon_mass": 1,
            "periodic_boundary": True,
        }
        super().__init__(self.default_constants, constants)
        self.dh_qc_dzc_inds = None
        self.dh_qc_dzc_mels = None
        self.dh_qc_dzc_shape = None

    def initialize_constants_model(self):
        N = self.constants.get("N", self.default_constants.get("N"))
        w = self.constants.get("w", self.default_constants.get("w"))
        phonon_mass = self.constants.get(
            "phonon_mass", self.default_constants.get("phonon_mass")
        )
        self.constants.num_quantum_states = N
        self.constants.num_classical_coordinates = N
        self.constants.classical_coordinate_weight = w * np.ones(N)
        self.constants.classical_coordinate_mass = phonon_mass * np.ones(N)

    def initialize_constants_h_q(self):
        J = self.constants.get("J", self.default_constants.get("J"))
        periodic_boundary = self.constants.get(
            "periodic_boundary", self.default_constants.get("periodic_boundary")
        )
        self.constants.nearest_neighbor_lattice_hopping_energy = J
        self.constants.nearest_neighbor_lattice_periodic_boundary = periodic_boundary

    def initialize_constants_h_qc(self):
        N = self.constants.get("N", self.default_constants.get("N"))
        w = self.constants.get("w", self.default_constants.get("w"))
        g = self.constants.get("g", self.default_constants.get("g"))
        h = self.constants.classical_coordinate_weight
        self.constants.diagonal_linear_coupling = np.diag(
            g * w * np.sqrt(h / w) * np.ones(N)
        )

    def initialize_constants_h_c(self):
        N = self.constants.get("N", self.default_constants.get("N"))
        w = self.constants.get("w", self.default_constants.get("w"))
        self.constants.harmonic_oscillator_frequency = w * np.ones(N)

    h_q = ingredients.nearest_neighbor_lattice_h_q
    dh_c_dzc = ingredients.harmonic_oscillator_dh_c_dzc
    h_c = ingredients.harmonic_oscillator_h_c
    h_qc = ingredients.diagonal_linear_h_qc
    dh_qc_dzc = ingredients.diagonal_linear_dh_qc_dzc
    init_classical = ingredients.harmonic_oscillator_boltzmann_init_classical
    hop_function = ingredients.harmonic_oscillator_hop_function
    linear_h_qc = True
    initialization_functions = [
        initialize_constants_model,
        initialize_constants_h_c,
        initialize_constants_h_qc,
        initialize_constants_h_q,
    ]
