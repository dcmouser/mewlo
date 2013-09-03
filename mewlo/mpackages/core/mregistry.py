"""
mregistry.py
This module contains classes and functions for managing a component/service registry.

"""


# helper imports
from helpers.registry.registry import Component, ComponentRegistry

# python imports








class MewloComponent(Component):
    """The derived Component."""

    def __init__(self, mewlosite, features, obj):
        """Constructor."""
        # partent constructor
        super(MewloComponent, self).__init__(features, obj)
        # init
        self.mewlosite = mewlosite



class MewloComponentRegistry(ComponentRegistry):
    """Derived Component Registry."""

    def __init__(self, mewlosite):
        """Constructor."""
        # partent constructor
        super(MewloComponentRegistry, self).__init__()
        # init
        self.mewlosite = mewlosite
