"""
mewlotestplugin_mpack.py
This file manages a test pack, meant to be autodiscovered via setup tools entry points
"""


# mewlo imports
from mewlo.mpacks.core.pack.mpackworker import MewloPackWorker




class SetupToolsPlugin_MewloPackWorker(MewloPackWorker):
    """
    The SetupToolsPlugin_MewloPackWorker class defines a test mewlo "pack" aka extension/plugin/addon.
    """


    def __init__(self, pack):
        # parent constructor
        super(SetupToolsPlugin_MewloPackWorker, self).__init__(pack)



    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        str = " "*indent + "Mewlo SetupToolsPlugin_MewloPackWorker v2 reporting in.\n"
        return str


