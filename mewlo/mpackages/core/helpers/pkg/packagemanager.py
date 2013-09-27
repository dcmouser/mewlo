"""
packagemanager.py
This file supports discovery and loading of modules by path and filename pattern

Note that our term "package" here is not referring to python packages (directories).

The package system here is made up of 3 classes:

    * PackageManager - holds a list of Packages.
    * Package - a thin wrapper around a package object.
    * PackageObject - the object that will be subclassed to do real work.

The Package is the thing that is autocreated on discovery of a .json definition file.
It will be instantiated even if this extension is disabled.

The PackageObject is only instantiated when the extension is enabled.

When coding a new plugin/extension, ONLY a derived PackageObject class would be created.

"""


# helper imports
from ..callables import importmodule_bypath
from ..event.event import EFailure

# python imports
import imp
import fnmatch
import os




class PackageManager(object):
    """
    The PackageManager is a class that can be used to dynamically find modules by path and filename pattern.  It manages a collection of Package objects that represent addonsm, etc.
    It's useful for plugin-discovery type things.
    """

    # class-wide dictionary of module imports, to avoid multiple dynamic-code-importing
    classwide_packagemodules = {}


    def __init__(self):
        # stuff
        self.dirlist = []
        self.filepatternsuffix = ''
        self.setuptools_entrypoint_groupname = ''
        # package collection
        self.packages = []


    def set_directories(self, dirlist):
        self.dirlist = dirlist

    def set_filepatternsuffix(self, filepatternsuffix):
        self.filepatternsuffix = filepatternsuffix

    def set_setuptools_entrypoint_groupname(self, setuptools_entrypoint_groupname):
        self.setuptools_entrypoint_groupname = setuptools_entrypoint_groupname


    def create_package(self, filepath):
        """Create a child package; subclasses will reimplement this to use their preferred child class."""
        return Package(self, filepath)



    def startup(self, eventlist):
        """Scan for packages and instantiate and start them up."""
        self.discover_packages()
        #
        self.loadinfos_packages()
        #
        self.instantiate_packages()
        #
        self.startup_packages()


    def shutdown(self):
        """Shutdown the packages."""
        self.shutdown_packages()



    def discover_packages(self):
        """Scan all package directories and discover packages."""

        # init
        packagefilepaths = []
        filepattern = self.calc_packageinfofile_pattern()
        # remove any EXISTING packages
        self.packages = []
        # first find all files
        for dirpath in self.dirlist:
            packagefilepaths += self.findfilepaths(dirpath, filepattern)
        # setup tools entrypoint loading?
        packagefilepaths += self.discover_setuptools_entrypoints_packagefilepaths()
        # now for each file, create a package from it
        for filepath in packagefilepaths:
            self.createadd_package_frominfofile(filepath)

    def loadinfos_packages(self):
        """Load all the info files."""
        self.load_package_infofiles()

    def instantiate_packages(self):
        """Actually import code modules and instantiate package objects."""
        self.load_package_codemodules()
        self.startup_packages()


    def startup_packages(self):
        """Startup the packages."""
        for package in self.packages:
            package.startup()

    def shutdown_packages(self):
        """Shutdown the packages."""
        for package in self.packages:
            package.shutdown()






    def createadd_package_frominfofile(self, infofilepath):
        """Given a path to an infofile, create a package from it."""
        pkg = self.create_package(infofilepath)
        if (pkg != None):
            self.packages.append(pkg)



    def calc_packageinfofile_pattern(self):
        """Given self.filepatternsuffix we create the file match pattern that describes the json info files we need to look for."""
        return '*_' + self.filepatternsuffix + '.json'


    def findfilepaths(self, dirpath, filepattern):
        """Find recursive list of filepaths matching pattern."""
        filepaths = []
        for path, dirs, files in os.walk(os.path.abspath(dirpath)):
            for filename in fnmatch.filter(files, filepattern):
                filepaths.append(os.path.join(path, filename))
        return filepaths







    def discover_setuptools_entrypoints_packagefilepaths(self):
        """Discover any setuptools based entry-point plugins that are exposing their info."""
        if (self.setuptools_entrypoint_groupname == ''):
            return []
        # init
        infofilepaths = []
        filepattern = self.calc_packageinfofile_pattern()
        #
        # ok we found some so let's try
        import pkg_resources
        import os
        #
        for entrypoint in pkg_resources.iter_entry_points(group=self.setuptools_entrypoint_groupname):
            # Ok get the entrypoint details
            entrypoint_fullname = entrypoint.name
            entrypoint_basename = entrypoint_fullname.split('.')[0]
            entrypoint_obj = entrypoint.load()
            # if entrypoint_obj is a callable, call it to get data, otherwise it IS the data alread
            if (hasattr(entrypoint_obj, '__call__')):
                entrypoint_data = entrypoint_obj()
            else:
                entrypoint_data = entrypoint_obj
            # debug
            #print "---------> GOT AN ENTRYPOINT OF "+str(entrypoint_obj)+" named: "+entrypoint_fullname + " (" + entrypoint_basename + ") with data: "+str(entrypoint_data)+"\n"
            # ok now let's handle it
            if (entrypoint_basename == 'infofiles'):
                # it's giving us info file (or list of them), so we append to filepaths
                if (isinstance(entrypoint_data, basestring)):
                    entrypoint_data = [ enrtypoint_data ]
                infofilepaths += entrypoint_data
            elif (entrypoint_basename == 'infofiledirs'):
                # it's giving us a directory (or list of them) to scan, so scan and add all in their
                if (isinstance(entrypoint_data, basestring)):
                    entrypoint_data = [ entrypoint_data ]
                for apath in entrypoint_data:
                    infofilepaths += self.findfilepaths(apath, filepattern)
            elif (entrypoint_basename == 'moduleforpath'):
                # it's giving us a module (or list of them) to resolve directories from and then treat as infofiledirs
                if (not hasattr(entrypoint_data, '__iter__')):
                    entrypoint_data = [ entrypoint_data ]
                for amod in entrypoint_data:
                    apath = os.path.abspath(os.path.dirname(amod.__file__))
                    infofilepaths += self.findfilepaths(apath, filepattern)
            else:
                # error bad directive in entry_point
                emsg = "While trying to load advertised setuptools entrypoints for Mewlo plugins (group='"+self.setuptools_entrypoint_groupname+"'), encountered an enrtypoint key value '"+entrypoint_fullname+"' that was not understood."
                emsg += " Full entrypoint line: "+str(entrypoint)+"."
                emsg += " Note that this line causing the error will most likely be located in a python EGG of an INSTALLED site-package; in the egg's setup.py or compiled into entry_points.txt."
                raise Exception(emsg)
        #
        return infofilepaths


















    def load_package_infofiles(self):
        """Load the infofiles for all packages found."""
        for package in self.packages:
            package.load_infofile()


    def load_package_codemodules(self):
        """Load the code modules for all packages found."""
        for package in self.packages:
            if (package.readytoloadcode):
                package.load_codemodule()


    def loadimport(self, path):
        """Dynamically load an importbypath (or returned cached value of previous import)."""
        dynamicmodule = None

        # not in our cache? then we have to load it
        if (not path in PackageManager.classwide_packagemodules):
            # first we check if path is blank or does not exist
            if (path == ''):
                return None, EFailure("Failed to load import by path '{0}', because a blank path was specified.".format(path))
            elif (not os.path.isfile(path)):
                return None, EFailure("Failed to load import by path '{0}', because that file does not exist.".format(path))
            else:
                # then load it dynamically
                dynamicmodule, failure = importmodule_bypath(path)
                if (failure != None):
                    return None, failure

            # now add it to our class-wide cache, so we don't try to reload it again
            PackageManager.classwide_packagemodules[path] = dynamicmodule

        # return it
        return PackageManager.classwide_packagemodules[path], None











    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = " "*indent + "PackageManager reporting in.\n"
        indent += 1
        outstr += " "*indent + "Directories to scan:\n"
        for dirpath in self.dirlist:
            outstr += " "*indent + " "+dirpath + "\n"
        outstr += self.debug_packages(indent)
        return outstr


    def debug_packages(self, indent=0):
        """Helper debug function.  Return indented debug of child packages."""
        outstr = " "*indent + str(len(self.packages)) + " packages found.\n\n"
        indent += 1
        for package in self.packages:
            outstr += package.dumps(indent+1) + "\n"
        return outstr


