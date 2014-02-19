"""
manager.py

A base class for high-level site-helping managers.
"""


# mewlo imports
import manager




class MewloModelManager(manager.MewloManager):
    """Manager class specialized to manage a database model class."""

    def __init__(self, mewlosite, debugmode, modelclass):
        """construct and initialize the stored modelclass that we manage."""
        super(MewloModelManager,self).__init__(mewlosite, debugmode)
        self.modelclass = modelclass


    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = " "*indent + "MewloModelManager ({0}) which manages model class '{1}' reporting in.\n".format(self.__class__.__name__, self.modelclass.__name__)
        return outstr


