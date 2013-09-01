"""
setup.py

This file defines setup functions for the mewlo setuptools based test plugin, which is used to test one way of autodiscovering plugins for mewlo.

See https://pypi.python.org/pypi/zest.releaser/3.3#entrypoints-documentation
See http://bashelton.com/2009/04/setuptools-tutorial/#advanced_options-entry_points
"""


# helper imports
from setuptools import setup, find_packages








setup (

    # information that may unfortunately be duplicative of the json info file data, so let's try to read it automatically


    name = "MewloTestPlugin",
    version = "0.1",
    description="Test plugin for Mewlo.",
    long_description="""\
This is a test plugin for Mewlo
Designed to be discovered with setup tools entry_points feature.
""",
    author="mouser@donationcoder.com",
    author_email="mouser@donationcoder.com",
    url="http://www.melo.com.com/",

    #package_dir = {'': 'src'}, # See packages below
    #package_data = {'': ['*.xml']},
    packages = find_packages(exclude="test"),
    # Use this line if you've uncommented package_dir above.
    #packages = find_packages("src", exclude="tests"),

    entry_points = {
        'mewlo.packages':
            [
            # we could pass a list of explicit info file paths using a helper function
            #'infofiles = mewlotestplug.discoveryhelper:get_infofiles',
            # or we could also pass a list of directories, using a helper function
            #'infofiledirs = mewlotestplug.discoveryhelper:get_infofiledirs',
            # or the simplest way requires no helper functions, just specify a modeule, and the directory where that module lives (and its subdirs) will be scanned for json info files
            # note that it doesnt matter what specific module we path here, the only thing that will be extracted is its DIRECTORY
            'modulesforpath = mewlotestplug.mewlotestplugin_mpackage',
            # note that we can specify multiple entries here by adding a dotted part to the key, which is otherwise ignored.
            # e.g. 'modulesforpath.two = mewlotestplug.mewlotestplugin_mpackage2',
            ]
        },

    # for setup tools automated installation
    download_url = "http://www.mewlo.com/downloads/addons/mewlotestplugin",

    # it may be important to pass zip_safe = False so that Mewlo can find files
    zip_safe = False
)











