"""
mpackagemanager.py
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


# mewlo imports
from ..helpers.callables import importmodule_bypath
from ..eventlog.mevent import EFailure, EDebug
from ..helpers.misc import get_value_from_dict, append_text
from mpackage import MewloPackage
from ..manager import manager

# python imports
import imp
import fnmatch
import os













class MewloPackageManager(manager.MewloManager):
    """
    The PackageManager is a class that can be used to dynamically find modules by path and filename pattern.  It manages a collection of Package objects that represent addonsm, etc.
    It's useful for plugin-discovery type things.
    """

    # class constants
    DefMewlo_Package_filepatternsuffix = 'mpackage'

    # class-wide dictionary of module imports, to avoid multiple dynamic-code-importing
    classwide_packagemodules = {}


    def __init__(self):
        # stuff
        super(MewloPackageManager,self).__init__()
        self.dirlist = []
        self.filepatternsuffix = ''
        self.setuptools_entrypoint_groupname = ''
        self.packagesettings = {}
        self.default_packagesettings = {}
        # package collection
        self.packages = []
        # set file pattern of mewlo package files
        self.set_filepatternsuffix(self.DefMewlo_Package_filepatternsuffix)
        # set setuptools entrypoint groupname
        self.set_setuptools_entrypoint_groupname('mewlo.packages')



    def startup(self, mewlosite, eventlist):
        """Any initial startup stuff to do?"""
        super(MewloPackageManager,self).startup(mewlosite,eventlist)
        # discover the packages in the package directories
        failures = []
        self.discover_packages(eventlist)
        # ok now that we have disocvered the packages, we walk them and apply any settings the might enable or disable them
        for package in self.packages:
            failure = self.startup_package_auto(mewlosite, package, eventlist)
            if (failure != None):
                # if we get a hard failure here, we add it to our list of failures, and to the eventlist
                eventlist.add(failure)
                failures.append(failure)
        # return failures
        return failures




    def shutdown(self):
        """Shutdown the packages."""
        super(MewloPackageManager,self).shutdown()
        for package in self.packages:
            package.shutdown()






    def set_directories(self, dirlist):
        self.dirlist = dirlist

    def set_filepatternsuffix(self, filepatternsuffix):
        self.filepatternsuffix = filepatternsuffix

    def set_setuptools_entrypoint_groupname(self, setuptools_entrypoint_groupname):
        self.setuptools_entrypoint_groupname = setuptools_entrypoint_groupname

    def set_packagesettings(self, packagesettings):
        self.packagesettings = packagesettings

    def set_default_packagesettings(self, default_packagesettings):
        self.default_packagesettings = default_packagesettings


    def create_package(self, filepath):
        """Create an appropriate child package."""
        return MewloPackage(self, filepath)


    def createadd_package_frominfofile(self, infofilepath):
        """Given a path to an infofile, create a package from it."""
        pkg = self.create_package(infofilepath)
        if (pkg != None):
            self.packages.append(pkg)
            # load the info file related to it
            pkg.load_infofile()
        return pkg





    def get_mewlosite(self):
        return self.mewlosite




    def discover_packages(self, eventlist):
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
            # create the package wrapper from the file
            pkg = self.createadd_package_frominfofile(filepath)




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
















    def loadimport(self, path):
        """Dynamically load an importbypath (or returned cached value of previous import)."""
        dynamicmodule = None

        # not in our cache? then we have to load it
        if (not path in MewloPackageManager.classwide_packagemodules):
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
            MewloPackageManager.classwide_packagemodules[path] = dynamicmodule

        # return it
        return MewloPackageManager.classwide_packagemodules[path], None






    def get_settings_forpackage(self, packageid):
        """Given a package id, lookup its settings."""
        retv = get_value_from_dict(self.packagesettings,packageid,{})
        return retv



    def startup_package_auto(self, mewlosite, package, eventlist):
        """Before we instantiate a package, we preprocess it using our settings, which may disable/enabe them."""
        # let's see if user WANTS this package enabled or disabled based on settings
        (flag_enable, reason) = self.want_enable_package(package, eventlist)
        # if they want it enabled, lets see if it meets initial dependency check if not, its a failure
        if (flag_enable):
            (dependencies_met, failurereason) = self.check_package_dependencies(package, None, [])
            if (not dependencies_met):
                # dependency fail, disable it and return the dependency error
                flag_enable = False
                package.do_enabledisable(mewlosite, flag_enable, reason, eventlist)
                return EFailure(failurereason)
        failure = package.do_enabledisable(mewlosite, flag_enable, reason, eventlist)
        return failure


    def want_enable_package(self, package, eventlist):
        """Do settings say to disable this package? Return tuple of (flag_enable, reasonstring)."""
        packageid = package.get_infofile_property(MewloPackage.DEF_INFOFIELD_uniqueid)
        #
        reason = "n/a"
        # is the package REQUIRED?
        if (package.get_infofile_property(MewloPackage.DEF_INFOFIELD_required)):
            flag_enable = True
            reason = "required package"
        else:
            # get any settings for the package
            packagesettings = self.get_settings_forpackage(packageid)
            flag_enable = get_value_from_dict(packagesettings,MewloPackage.DEF_INFOFIELD_enabled)
            if (flag_enable==None):
                flag_enable = get_value_from_dict(self.default_packagesettings, MewloPackage.DEF_INFOFIELD_enabled)
                reason = "default enable/disable state for packages"
            else:
                if (flag_enable):
                    reason = "explicitly enabled in site settings"
                else:
                    reason = "explicitly disabled in site settings"
        return (flag_enable, reason)



    def will_enable_package_byid(self, packageid, requirer, assumegoodlist):
        """Check if package will be enabled, by id."""
        package = self.findpackage_byid(packageid)
        if (package==None):
            return (False,"Package not found".format(packageid))
        eventlist = []
        (flag_enable, reason) = self.want_enable_package(package, eventlist)
        if (flag_enable):
            (dependencies_met, reason) = self.check_package_dependencies(package, requirer, assumegoodlist)
            if (not dependencies_met):
                flag_enable = false
        return (flag_enable, reason)


    def check_package_dependencies(self, package, requirer, assumegoodlist):
        """Check whether this package has its dependenices met.  Return tuple (dependencies_met, reasontext)."""
        reason = ""
        result = True
        packageid = package.get_infofile_property(MewloPackage.DEF_INFOFIELD_uniqueid)
        if (requirer==None):
            requirer = "Package '{0}'".format(packageid)
        # is this package already on our assumed good list? if so just return and and say good (this avoids circular dependencies)
        if (packageid in assumegoodlist):
            return (True,"")
        # add this packageid to our list of assumed good
        assumegoodlist.append(packageid)
        # first get the list of what this package requires
        requiredict = package.get_infofile_property(MewloPackage.DEF_INFOFIELD_requires)
        if (requiredict != None):
            # ok let's check for required PACKAGES (not python packages but our packages)
            requiredpackages = get_value_from_dict(requiredict, MewloPackage.DEF_INFOFIELD_requiredpackages)
            if (requiredpackages != None):
                # ok we need to check required packages
                # ATTN: TODO - we may want to check version infor here later
                for packageid in requiredpackages:
                    (required_package_enabled, thisreason) = self.will_enable_package_byid(packageid, requirer, assumegoodlist)
                    if (not required_package_enabled):
                        result = False
                        thisreason = "{0} depends on package '{1}', which is not enabled because: ".format(requirer, packageid) + thisreason
                        reason = append_text(reason, thisreason, " ;")
        # if we fell down to here, all requirements are met
        return (result, reason)




    def findpackage_byid(self, packageid):
        """Return the package object for the package specified by id, or None if not found."""
        #ATTN: TODO - cache this info in a dictionary for faster lookup?
        for package in self.packages:
            apackageid = package.get_infofile_property(MewloPackage.DEF_INFOFIELD_uniqueid)
            if (packageid == apackageid):
                return package
        return None



    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = " "*indent + "PackageManager reporting in ({0} packages found).\n".format(len(self.packages))
        indent += 1
        outstr += " "*indent + "Directories scanned:\n"
        for dirpath in self.dirlist:
            outstr += " "*indent + " "+dirpath + "\n"
        outstr += "\n"
        #
        indent += 1
        for package in self.packages:
            outstr += package.dumps(indent+1) + "\n"
        return outstr


