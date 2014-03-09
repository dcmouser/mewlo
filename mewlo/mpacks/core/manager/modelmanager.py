"""
manager.py

A base class for high-level site-helping managers.
"""


# mewlo imports
import manager




class MewloModelManager(manager.MewloManager):
    """Manager class specialized to manage a database model class."""

    # class constants
    description = "Handles a database model"
    typestr = "core"


    def __init__(self, mewlosite, debugmode, modelclass, flag_set_objmanager):
        """construct and initialize the stored modelclass that we manage."""
        super(MewloModelManager,self).__init__(mewlosite, debugmode)
        # record the modelclass as the modelclass we use
        self.modelclass = modelclass
        if (flag_set_objmanager):
            # tell the modelclass that we are the objmanager for it
            modelclass.set_objectmanager(self)


    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = " "*indent + "MewloModelManager ({0}) which manages model class '{1}' reporting in.\n".format(self.__class__.__name__, self.modelclass.__name__)
        outstr += self.dumps_description(indent+1)
        return outstr


