"""
setup.py

This file defines setup functions for the mewlo setuptools based test plugin, which is used to test one way of autodiscovering plugins for mewlo.

See https://pypi.python.org/pypi/zest.releaser/3.3#entrypoints-documentation
See http://bashelton.com/2009/04/setuptools-tutorial/#advanced_options-entry_points
"""


# setuptools helper imports
from setuptools import setup, find_packages


# mewlo helpers
from mewlo.externaltools.setuptoolhelpers import shelp_readfile_asjson, dvalordef





# setup tools wants some author and other information that may unfortunately be duplicative of the json info file data for our plugin, so let's try to read it automatically from that file
infofilepath = 'mewlosetuptoolsplugintest/mewlotestplug_mpackage.json'
infofiledict, failure = shelp_readfile_asjson(infofilepath)







setup (

    name = dvalordef(infofiledict,'nicename'),
    version = dvalordef(infofiledict,'version'),
    description = dvalordef(infofiledict,'label'),
    long_description = dvalordef(infofiledict,'description'),
    author = dvalordef(infofiledict,'author'),
    author_email = dvalordef(infofiledict,'authoremail',''),
    url = dvalordef(infofiledict,'url.home'),
    download_url = dvalordef(infofiledict,'url.download',''),

    # from example code
    #package_dir = {'': 'src'}, # See packages below
    #packages = find_packages("src", exclude="tests"),

		# important to pick up our json info files
    package_data = {'': ['*.json']},

    packages = find_packages(exclude="test"),

    entry_points = {
        'mewlo.packages':
            [
            # we could pass a list of explicit info file paths using a helper function
            #'infofiles = mewlosetuptoolsplugintest.discoveryhelper:get_infofiles',
            # or we could also pass a list of directories, again using a helper function
            #'infofiledirs = mewlosetuptoolsplugintest.discoveryhelper:get_infofiledirs',

            # or the simplest way requires no helper functions, just specify a modeule, and the directory where that module lives (and its subdirs) will be scanned for json info files
            # note that it doesnt matter what specific module we path here, the only thing that will be extracted is its DIRECTORY
            'moduleforpath = mewlosetuptoolsplugintest.mewlotestplugin_mpackage',

            # note that we can specify multiple entries here by adding a dotted part to the key, which is otherwise ignored.
            # e.g. 'modulesforpath.two = mewlosetuptoolsplugintest.mewlotestplugin_mpackage2',
            ]
        },



    # it may be important to pass zip_safe = False so that Mewlo can find files
    zip_safe = False,
)






























