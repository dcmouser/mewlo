"""
core_mpack.py
This file "manages" the core Mewlo classes.

By "manage" we mean the following:

All code in mewlo, both the core code, and any 3rd party addons/plugins/extensions, is considered to be "managed" by a MewloPack.
The MewloPack provides information about the version of the code release and associated information suitable for doing online update checking,
 as well as author information, and dependency information between packs, etc.

So this Core_MewloPackObject is the "manager" or owner of all core mewlo code.
It doesn't actually *do* anything -- but does describe and version the core code.

"""



# mewlo imports
from pack import mpackobject




class Core_MewloPackObject(mpackobject.MewloPackObject):
    """
    The Core_MewloPack class manages the core mewlo code
    """

    def __init__(self, pack):
        # parent constructor
        super(Core_MewloPackObject, self).__init__(pack)


    def startup(self, mewlosite, eventlist):
        # called by Mewlo system when it's ready for us to do any setup stuff
        # return failure if any, or None on success
        retv = self.setup_everything(mewlosite, eventlist)
        if (retv != None):
            return retv
        #
        return None


    def shutdown(self):
        # called by Mewlo system when it's ready for us to do any shutdown
        super(Core_MewloPackObject, self).shutdown()
        return None





    def setup_everything(self, mewlosite, eventlist):
        # called by Mewlo system when it's ready for us to do any setup stuff
        # let's register database classes
        ##self.setup_databaseclasses()
        return None




    def setup_databaseclasses(self):
        # called by Mewlo system when it's ready for us to do any setup stuff
        return None





    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        str = " "*indent + "Core_MewloPackObject reporting in.\n"
        return str

