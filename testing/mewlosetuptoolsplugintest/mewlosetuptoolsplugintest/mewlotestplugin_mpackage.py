"""
mewlotestplugin_mpackage.py
This file manages a test package, meant to be autodiscovered via setup tools entry points
"""


# mewlo imports
from mewlo.mpackages.core.package.mpackageobject import MewloPackageObject




class SetupToolsPlugin_MewloPackageObject(MewloPackageObject):
    """
    The SetupToolsPlugin_MewloPackageObject class defines a test mewlo "package" aka extension/plugin/addon.
    """


    def __init__(self, package):
        # parent constructor
        super(SetupToolsPlugin_MewloPackageObject, self).__init__(package)



    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        str = " "*indent + "Mewlo SetupToolsPlugin_MewloPackageObject reporting in.\n"
        return str

