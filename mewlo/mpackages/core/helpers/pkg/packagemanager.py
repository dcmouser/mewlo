"""
packagemanager.py
This file supports discovery and loading of modules by path and filename pattern
"""




# python imports
import imp
import fnmatch
import os

# helper imports
from ..callables import importmodule_bypath
from ..event.event import EFailure





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
        self.filepatternsuffix = ""
        # package collection
        self.packages = []


    def set_directories(self, dirlist):
        self.dirlist = dirlist

    def set_filepatternsuffix(self, filepatternsuffix):
        self.filepatternsuffix = filepatternsuffix


    def create_package(self, filepath):
        """Create a child package; subclasses will reimplement this to use their preferred child class."""
        return Package(self,filepath)



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
        # now for each file, create a package from it
        for filepath in packagefilepaths:
            self.createadd_package_frominfofile(filepath)



    def createadd_package_frominfofile(self, infofilepath):
        """Given a path to an infofile, create a package from it."""
        pkg = self.create_package(infofilepath)
        if (pkg != None):
            self.packages.append(pkg)



    def loadinfos_packages(self):
        """Load all the info files."""
        self.load_package_infofiles()



    def instantiate_packages(self):
        """Actually import code modules and instantiate package objects."""
        self.load_package_codemodules()


    def calc_packageinfofile_pattern(self):
        """Given self.filepatternsuffix we create the file match pattern that describes the json info files we need to look for."""
        return "*_" + self.filepatternsuffix+".json"


    def findfilepaths(self, dirpath, filepattern):
        """Find recursive list of filepaths matching pattern."""
        filepaths = []
        for path, dirs, files in os.walk(os.path.abspath(dirpath)):
            for filename in fnmatch.filter(files, filepattern):
                filepaths.append(os.path.join(path, filename))
        return filepaths


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
            if (path == ""):
                return None, EFailure("Failed to load import by path '"+path+"', because a blank path was specified.")
            elif (not os.path.isfile(path)):
                return None, EFailure("Failed to load import by path '"+path+"', because that file does not exist.")
            else:
                # then load it dynamically
                dynamicmodule, failure = importmodule_bypath(path)
                if (failure != None):
                    return None, failure

            # now add it to our class-wide cache, so we don't try to reload it again
            PackageManager.classwide_packagemodules[path] = dynamicmodule

        # return it
        return PackageManager.classwide_packagemodules[path], None



    def debug(self, indentstr=""):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = indentstr+"PackageManager reporting in.\n"
        indentstr+=" "
        outstr += indentstr+"Directories to scan:\n"
        for dirpath in self.dirlist:
            outstr += indentstr+" "+dirpath+"\n"
        outstr += self.debug_packages(indentstr)
        return outstr


    def debug_packages(self, indentstr=""):
        """Helper debug function.  Return indented debug of child packages."""
        outstr = indentstr+"Packages found:\n"
        indentstr+=" "
        if (len(self.packages)==0):
            outstr += indentstr+"None.\n"
        for package in self.packages:
            outstr += package.debug(indentstr+" ")+"\n"
        return outstr



