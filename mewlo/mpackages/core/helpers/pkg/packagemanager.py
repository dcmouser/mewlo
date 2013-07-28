# packagemanager.py
# This file supports discovery and loading of modules by path and filename pattern

# python libraries
import imp
import fnmatch
import os
import sys
import traceback




class PackageManager(object):
    """
    The PackageManager is a class that can be used to dynamically find modules by path and filename pattern, and load them.
    It's useful for plugin-discovery type things
    """

    # class-wide dictionary of module imports, to avoid multiple dynamic-code-importing
    classwide_packagemodules = {}


    def __init__(self):
        # stuff
        self.dirlist = []
        self.filepatternsuffix = ""
        # package list
        self.packages = []


    def set_directories(self, dirlist):
        self.dirlist = dirlist

    def set_filepatternsuffix(self, filepatternsuffix):
        self.filepatternsuffix = filepatternsuffix


    def create_package(self, filepath):
        """Create a child package; subclasses will reimplement this to use their preferred child class"""
        return Package(self,filepath)

    def discover_packages(self):
        """Scan all package directories and discover packages"""
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
        """Given a path to an infofile, create a package from it"""
        pkg = self.create_package(infofilepath)
        if (pkg != None):
            self.packages.append(pkg)

    def loadinfos_packages(self):
        # now let's go ahead and load all the info files
        self.load_package_infofiles()

    def instantiate_packages(self):
        """Actually import code modules and instantiate package objects"""
        self.load_package_codemodules()


    def calc_packageinfofile_pattern(self):
        return "*_"+self.filepatternsuffix+".json"


    def findfilepaths(self, dirpath, filepattern):
        """Find recursive list of filepaths matching pattern"""
        filepaths = []
        for path, dirs, files in os.walk(os.path.abspath(dirpath)):
            for filename in fnmatch.filter(files, filepattern):
                filepaths.append(os.path.join(path, filename))
        return filepaths


    def load_package_infofiles(self):
        """Load the infofiles for all packages found"""
        for package in self.packages:
            package.load_infofile()


    def load_package_codemodules(self):
        """Load the code modules for all packages found"""
        for package in self.packages:
            if (package.readytoloadcode):
                package.load_codemodule()


    def loadimport(self, path):
        """Dynamically load an importbypath (or returned cached value of previous import)"""
        dynamicmodule = None
        errorstr = ""

        # not in our cache? then we have to load it
        if (not path in PackageManager.classwide_packagemodules):
            # first we check if path is blank or does not exist
            if (path==""):
                errorstr = "Blank path specified."
            elif (not os.path.isfile(path)):
                errorstr = "File does not exist ("+path+")."
            else:
                # get name+extension of file, for import module info
                # ok now load it dynamically
                (dynamicmodule, errorstr) = self.DoImportModuleByPath(path)

            # now add it to our class-wide cache, so we don't try to reload it again
            PackageManager.classwide_packagemodules[path] = dynamicmodule

        # return it
        return (PackageManager.classwide_packagemodules[path],errorstr)




    def DoImportModuleByPath(self, path):
        return self.DoImportModuleByPath_Version1(path)



    def DoImportModuleByPath_Version1(self, path):
        """Load a python module import by explicit path; version1 uses imp.load_source"""
        dynamicmodule = None
        errorstr = ""

        name, ext = os.path.splitext(os.path.basename(path))
        modulename = "DynamicallyLoadedPackage_"+name

        try:
            dynamicmodule = imp.load_source(modulename, path)
        except Exception as exp:
            errorstr = "Failure to load_source module ("+path+"): "+str(exp)+"; STACK TRACEBACK: "+traceback.format_exc()

        return (dynamicmodule, errorstr)


    def DoImportModuleByPath_Version2(self, path):
        """Load a python module import by explicit path; version2 uses find_module and load_module"""
        dynamicmodule = None
        errorstr = ""
        file = None

        # get name+path
        name, ext = os.path.splitext(os.path.basename(path))
        dirpath = os.path.dirname(path)

        # find the module
        try:
            (file, filename, data) = imp.find_module(name, [dirpath])
            if (not file):
                errorstr = "Failure to find module ("+path+")."
        except Exception as exp:
            errorstr = "Failure to find module ("+path+"): "+str(exp)
        # load it after find
        if (file):
            try:
                dynamicmodule = imp.load_module(name, file, filename, data)
            except Exception as exp:
                errorstr = "Failure to load module ("+path+"): "+str(exp)+"; STACK TRACEBACK: "+traceback.format_exc()
            file.close()
        # return it
        return (dynamicmodule, errorstr)


    def DoImportModuleByPath_Version3(self, path):
        """Load a python module import by explicit path; version3 appends to sys path"""
        dynamicmodule = None
        errorstr = ""

        # save previous sys path
        oldpath = sys.path

        #append path of new module to load
        dirpath = os.path.dirname(path)
        name, ext = os.path.splitext(os.path.basename(path))
        sys.path.append(dirpath)

        # do the import
        try:
            dynamicmodule = __import__(name)
        except Exception as exp:
            errorstr = "Failure to import package code module ("+path+"): "+str(exp)+"; STACK TRACEBACK: "+traceback.format_exc()

        # reset sys path
        sys.path = oldpath

        # return it
        return (dynamicmodule, errorstr)


    def debug(self, indentstr=""):
        outstr = indentstr+"PackageManager reporting in.\n"
        indentstr+=" "
        outstr += indentstr+"Directories to scan:\n"
        for dirpath in self.dirlist:
            outstr += indentstr+" "+dirpath+"\n"
        outstr += self.debug_packages(indentstr)
        return outstr

    def debug_packages(self, indentstr=""):
        outstr = indentstr+"Packages found:\n"
        indentstr+=" "
        if (len(self.packages)==0):
            outstr += indentstr+"None.\n"
        for package in self.packages:
            outstr += package.debug(indentstr+" ")+"\n"
        return outstr








class PackageObject(object):
    """
    The PackageObject class is the parent class for the actual 3rd party class that will be instantiated when a package is LOADED+ENABLED
    """

    def __init__(self, package):
        self.package = package


    def debug(self, indentstr=""):
        outstr = indentstr+"Base PackageObject reporting in.\n"
        return outstr


