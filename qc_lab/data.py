"""
Module defining the Data class.
"""

import numpy as np
import h5py


class Data:
    """
    The data object handles the collection of data from the dynamics driver.
    """

    def __init__(self):
        self.data_dict = {"seed": np.array([], dtype=int), "norm_factor": 0}

    def add_to_output_total_arrays(self, sim, state, t_ind):
        """
        Add data to the output total arrays.

        Args:
            sim: The simulation object containing settings and parameters.
            full_state: The full state object containing the current simulation state.
            t_ind: The current time index in the simulation.
        """
        # Check if the norm_factor is zero, if it is, save it from the state object.
        if self.data_dict["norm_factor"] == 0:
            if not (hasattr(state, "norm_factor")):
                raise ValueError(
                    "The state object does not have a norm_factor attribute."
                )
            self.data_dict["norm_factor"] = state.norm_factor
        for key, val in state.output_dict.items():
            if key in self.data_dict:
                self.data_dict[key][int(t_ind / sim.settings.dt_output_n)] = (
                    np.sum(val, axis=0) / self.data_dict["norm_factor"]
                )
            else:
                self.data_dict[key] = np.zeros(
                    (len(sim.settings.tdat_output), *np.shape(val)[1:]), dtype=val.dtype
                )
                self.data_dict[key][int(t_ind / sim.settings.dt_output_n)] = (
                    np.sum(val, axis=0) / self.data_dict["norm_factor"]
                )

    def add_data(self, new_data):
        """
        Add new data to the existing data dictionary.

        Args:
            new_data: A Data object containing the new data to be merged.
        """
        new_norm_factor = (
            new_data.data_dict["norm_factor"] + self.data_dict["norm_factor"]
        )
        for key, val in new_data.data_dict.items():
            if val is None:
                print(key, val)
            if key == "seed":
                self.data_dict[key] = np.concatenate(
                    (self.data_dict[key], val.flatten()), axis=0
                )
            elif key != "norm_factor":
                if key in self.data_dict:
                    self.data_dict[key] = (
                        self.data_dict[key] * self.data_dict["norm_factor"]
                        + val * new_data.data_dict["norm_factor"]
                    ) / new_norm_factor
                else:
                    self.data_dict[key] = val
        self.data_dict["norm_factor"] = new_norm_factor

    def save_as_h5(self, filename):
        """
        Save the data as an h5 archive.

        Args:
            filename: The name of the file to save the data to.
        """
        with h5py.File(filename, "w") as h5file:
            self._recursive_save(h5file, "/", self.data_dict)

    def load_from_h5(self, filename):
        """
        Load a data object from an h5 archive.

        Args:
            filename: The name of the file to load the data from.

        Returns:
            The Data object with the loaded data.
        """
        with h5py.File(filename, "r") as h5file:
            self._recursive_load(h5file, "/", self.data_dict)
        return self

    def _recursive_save(self, h5file, path, dic):
        """
        Recursively saves dictionary contents to an HDF5 group.

        Args:
            h5file: The HDF5 file object to save data into.
            path: The current path in the HDF5 file.
            dic: The dictionary to save.
        """
        for key, item in dic.items():
            if isinstance(item, (np.ndarray, np.int64, np.float64, str, bytes)):
                h5file[path + key] = item
            elif isinstance(item, dict):
                self._recursive_save(h5file, path + key + "/", item)
            elif isinstance(item, list):
                h5file[path + key] = np.array(item)
            else:
                raise ValueError(f"Cannot save {type(item)} type")

    def _recursive_load(self, h5file, path, dic):
        """
        Recursively loads dictionary contents from an HDF5 group.

        Args:
            h5file: The HDF5 file object to load data from.
            path: The current path in the HDF5 file.
            dic: The dictionary to populate with loaded data.
        """
        for key, item in h5file[path].items():
            if isinstance(item, h5py._hl.dataset.Dataset):
                dic[key] = item[()]
            elif isinstance(item, h5py._hl.group.Group):
                dic[key] = {}
                self._recursive_load(h5file, path + key + "/", dic[key])
