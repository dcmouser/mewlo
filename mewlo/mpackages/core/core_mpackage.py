"""
core_mpackage.py
This file "manages" the core Mewlo classes.

By "manage" we mean the following:

All code in mewlo, both the core code, and any 3rd party addons/plugins/extensions, is considered to be "managed" by a MewloPackage.
The MewloPackage provides information about the version of the code release and associated information suitable for doing online update checking,
 as well as author information, and dependency information between packages, etc.

So this Core_MewloPackageObject is the "manager" or owner of all core mewlo code.
It doesn't actually *do* anything -- but does describe and version the core code.

"""



# mewlo imports
import mpackage





class Core_MewloPackageObject(mpackage.MewloPackageObject):
    """
    The Core_MewloPackage class manages the core mewlo code
    """

    def __init__(self, package):
        # parent constructor
        super(Core_MewloPackageObject, self).__init__(package)


    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        str = " "*indent + "Core_MewloPackageObject reporting in.\n"
        return str

