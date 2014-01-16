"""
setup.py

This file defines setup functions for the mewlo setuptools-based test plugin, which is used to test one way of autodiscovering plugins for mewlo.
Setuptools is an optional python library which provides functionality for writing and discovering plugins, among other things.

See setuptoolshelpers.py for more information
"""

# python modules
import os

# mewlo helpers
from mewlo.externaltools.setuptoolhelpers import shelp_invoke_setuptools_setup


# the source path, typically the directory of this script
sourcepath = os.path.abspath(os.path.dirname(__file__))






# The two variable assignments below should be the only thing you need to change if you want to use this setup.py for another plugin/package

# setuptools wants some author and other information; this information will be read from our standard mewlo json file so we don't have to duplicate it; relative to sourcepath above
infofilepath_relative = 'mewlosetuptoolsplugintest/mewlotestplug_mpackage.json'

# setuptools entry_point_packages (see shelp_invoke_setuptools_setup) tells setuptools how to find us
entry_point_packages = [ 'moduleforpath = mewlosetuptoolsplugintest.mewlotestplugin_mpackage' ]

# alternative ways to specify setuptools entry points, which might be useful if one setuptools setup covers many plugins with their own json files
# these depend on a small module called setuptools_discoveryhelper
#entry_point_packages = [ 'infofiledirs = mewlosetuptoolsplugintest.setuptools_discoveryhelper:get_infofiledirs' ]
#entry_point_packages = [ 'infofiles = mewlosetuptoolsplugintest.setuptools_discoveryhelper:get_infofiles' ]




# call the setup tools setup function using data in the json file
shelp_invoke_setuptools_setup(sourcepath, infofilepath_relative, entry_point_packages)


























