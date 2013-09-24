"""
discoveryhelper.py

This file defines some helper functions for the mewlo setuptools based test plugin, which is used to test one way of autodiscovering plugins for mewlo.
We don't need this file if we choose to use the simple way of sepecify entry_points using 'moduleforpath'

"""



# exported function called from entry_points host


def get_infofiles():
    """This is the function that returns the list of info filesprovided by this setup-based addon."""
    import os
    thismoduledir = os.path.abspath(os.path.dirname(__file__))
    return [ thismoduledir+'/mewlotestplug_mpackage.json' ]



def get_infofiledirs():
    """This is the function that returns the list of dirs to scan for infofiles."""
    import os
    thismoduledir = os.path.abspath(os.path.dirname(__file__))
    return [ thismoduledir ]

