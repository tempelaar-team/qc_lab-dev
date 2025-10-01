"""
This module contains the Algorithm class.
"""

import copy
from qc_lab.constants import Constants


class Algorithm:
    """
    Algorithm class for defining and executing algorithm recipes.
    """

    def __init__(self, default_settings=None, settings=None):
        if settings is None:
            settings = {}
        if default_settings is None:
            default_settings = {}
        # Merge default settings with user-provided settings.
        settings = {**default_settings, **settings}
        # Construct a Constants object to hold settings.
        self.settings = Constants()
        # Put settings from the dictionary into the Constants object.
        for key, val in settings.items():
            setattr(self.settings, key, val)
        # Copy the recipes and output variables to ensure they are not shared
        # across instances.
        self.initialization_recipe = copy.deepcopy(self.initialization_recipe)
        self.update_recipe = copy.deepcopy(self.update_recipe)
        self.collect_recipe = copy.deepcopy(self.collect_recipe)

    initialization_recipe = []
    update_recipe = []
    collect_recipe = []

    def execute_recipe(self, sim, state, parameters, recipe):
        """
        Carry out the given recipe for the simulation by running
        each task in the recipe.
        """
        for func in recipe:
            state, parameters = func(sim, state, parameters)
        return state, parameters
