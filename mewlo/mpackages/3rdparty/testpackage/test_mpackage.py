"""
test_mpackage.py
This file manages a test package
"""


# mewlo imports
from mewlo.mpackages.core.mpackage import MewloPackageObject




class Test_MewloPackageObject(MewloPackageObject):
    """
    The Test_MewloPackage class defines a test mewlo "package" aka extension/plugin/addon.
    """


    def __init__(self, package):
        # parent constructor
        super(Test_MewloPackageObject, self).__init__(package)



    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        str = " "*indent + "Mewlo Test_MewloPackage reporting in.\n"
        return str

