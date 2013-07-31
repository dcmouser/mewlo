# core_mpackage.py
# This file manages the core Mewlo classes

# mewlo imports
from mewlo.mpackages.core.mpackage import MewloPackageObject



class Core_MewloPackageObject(MewloPackageObject):
    """
    The Core_MewloPackage class manages the core mewlo code
    """

    def __init__(self, package):
        super(Core_MewloPackageObject, self).__init__(package)
        pass


    def debug(self,indentstr=""):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        str = indentstr+"Core_MewloPackageObject reporting in.\n"
        return str

