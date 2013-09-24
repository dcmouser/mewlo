"""
core_mpackage.py
This file manages the core Mewlo classes
"""



# mewlo imports
# ATTN: 8/13/13 some of the ways we attempt to dynamically import our packages fails on relative imports..
# but why? i think because the path is not being added when the file is dynamically imported.
# this isn't a problem for core but it may very well be a problem for dynamically loaded plugin extensions that want to import relative files
# ATTN: TODO look into this -- it was working fine relative until we tried running unit tests

from mpackage import MewloPackageObject





class Core_MewloPackageObject(MewloPackageObject):
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

