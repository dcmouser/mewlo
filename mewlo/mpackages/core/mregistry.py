"""
mregistry.py
This module contains classes and functions for managing a component/service registry.

"""


# helper imports
from helpers.registry.registry import Component, ComponentRegistry

# python imports








class MewloComponent(Component):
    """The derived Component."""

    def __init__(self, id, owner, features, obj):
        """Constructor."""
        # partent constructor
        super(MewloComponent, self).__init__(id, owner, features, obj)



class MewloComponentRegistry(ComponentRegistry):
    """Derived Component Registry."""

    def __init__(self):
        """Constructor."""
        # partent constructor
        super(MewloComponentRegistry, self).__init__()


    def startup(self, mewlosite, eventlist):
        self.mewlosite = mewlosite
        # parent func
        super(MewloComponentRegistry, self).startup()

    def shutdown(self):
        # parent func
        super(MewloComponentRegistry, self).shutdown()