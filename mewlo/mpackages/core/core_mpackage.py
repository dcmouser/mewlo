# core_mpackage.py
# This file manages the core Mewlo classes

# mewlo imports
from mewlo.mpackages.core.mpackage import MewloPackageObject



class Core_MewloPackageObject(MewloPackageObject):
    """
    The Core_MewloPackage class manages the core mewlo code
    """

    def __init__(self, in_package):
        super(Core_MewloPackageObject, self).__init__(in_package)
        pass


    def debug(self,indentstr=""):
        str = indentstr+"Core_MewloPackageObject reporting in.\n"
        return str

