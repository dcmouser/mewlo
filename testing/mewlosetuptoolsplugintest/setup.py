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





# setup tools wants some author and other information that may unfortunately be
# duplicative of the json info file data for our plugin, so let's try to read
# it automatically from that file.
infofilepath = 'mewlosetuptoolsplugintest/mewlotestplug_mpackage.json'
infofiledict = shelp_readfile_asjson(infofilepath)







setup (

    name = dvalordef(infofiledict,'nicename'),
    version = dvalordef(infofiledict,'version'),
    description = dvalordef(infofiledict,'label'),
    long_description = dvalordef(infofiledict,'description'),
    author = dvalordef(infofiledict,'author'),
    author_email = dvalordef(infofiledict,'authoremail',''),
    url = dvalordef(infofiledict,'url.home'),
    download_url = dvalordef(infofiledict,'url.download',''),


		# tell the setuptools packager to pick up our json info files and include them in the setup package
    package_data = {'': ['*.json']},


    # see http://pythonhosted.org/distribute/setuptools.html#id9
    # if we used a subdirectory for source (e.g. 'src') then we would use the first form, otherwise the simpler second form
    #package_dir = {'': 'src'}, # See packages below
    #packages = find_packages("src", exclude="tests"),
    #
    packages = find_packages(exclude="test"),


    # we require mewlo to be installed? we normally do NOT enable this line as we test mewlo without officially "installing" it as a site-package
    #install_requires = ['mewlo>=0.1'],



    entry_points = {
        # the data specified for the entry point 'mewlo.packages' is the data that the mewlo plugin host system will receive.
        # it will parse this data in order to instantiate the addons/plugins/etc.
        # essentially what we provide here is simply information about the directory where this client plugin lives.
        # given the directory, the plugin host will find the standard "mpackage" system we use for mewlo plugins.
        # the mpackage approach basically uses a .json file for info about the plugin, and a matching _mpackage.py file
        # which implements the plugin.
        # One could contrast this approach with other python plugin systems using setuptool entrypoints, where the entrypoint
        # provides richer details about the plugin details.  In our case we want to use a single clean class system for
        # plugins, so our setuptools entrypoint is just used to tell mewlo additional directories to scan for plugins that are
        # installed independently and outside of the mewlo directory.
        'mewlo.packages':
            [
            # we could pass a list of explicit info file paths using a helper function
            #'infofiles = mewlosetuptoolsplugintest.discoveryhelper:get_infofiles',
            # or we could also pass a list of directories, again using a helper function
            #'infofiledirs = mewlosetuptoolsplugintest.discoveryhelper:get_infofiledirs',

            # or the simplest way requires no helper functions, just specify a module,
            # and the directory where that module lives (and its subdirs) will be scanned for json info files.
            # note that it doesn't matter what specific module we path here, the only thing that will be extracted is its DIRECTORY
            'moduleforpath = mewlosetuptoolsplugintest.mewlotestplugin_mpackage',

            # note that we can specify multiple entries here by adding a dotted part to the key, which is otherwise ignored.
            # e.g. 'modulesforpath.two = mewlosetuptoolsplugintest.mewlotestplugin_mpackage2',
            ]
        },



    # it's probably important to pass zip_safe = False so that Mewlo can find actual installed files rather than simulated files in a zip
    zip_safe = False,
)






























