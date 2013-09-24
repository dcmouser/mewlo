"""
discoveryhelper.py

This file defines some helper functions for the mewlo setuptools based test plugin, which is used to test one way of autodiscovering plugins for mewlo.
Note that they depend on using the __file__ macro, so this discoveryhelper.py module MUST be in the location where the mpackage source code is.

IMPORTANT: We don't need this file if we choose to use the simple way of sepecify entry_points using 'moduleforpath'.
In the test code I use, these functions are *not* called or used; they just exist as examples of alternate ways of telling the setuptools plugin which files are mpackage files.

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

