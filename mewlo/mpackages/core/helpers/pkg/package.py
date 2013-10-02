"""
package.py
Works with packagemanager.py to support our package/extension/addon system
"""


# mewlo imports
from ..misc import readfile_asjson

# helper imports
from ..event.event import EventList, EFailure
from ..exceptionplus import ExceptionPlus

# python imports
import json
import os



class Package(object):
    """
    The Package is a class represents a dynamically found module that can be used as an addon package.
    It is actually a fairly light-weight structure that:
        * loads a json info file with information about the "addon package".
        * dynamically loads(imports) a python code module specified by the json info file.
        * dynamically instantiates a PackageObject object from the above python code module.
    It is actually the PackageObject object that, once instantiated, does the work of the addon.
    So, the right way to think of a Package is as the bridge middleman responsible for instantiating a PackageObject addon.
    Additional features that the Package class provides:
        * displaying addon info, version info, update checking, etc.
        * handles dependency checking, etc.
    A Package also keeps an eventlist of any warnings or errors encountered while trying to instantiate the PackageObject.
    If an addon cannot be located/loaded/etc., the error information will be stores in this eventlist, and the addon will be disabled.
    """

    def __init__(self, packagemanager, filepath):
        # keep pointer to package manager
        self.packagemanager = packagemanager
        # found info (json) file defining the package
        self.infofilepath = filepath
        # dictionary acquired from info file
        self.infodict = None
        # imported module of code
        self.codemodule_path = ''
        self.codemodule = None
        self.packageobject = None
        #
        self.readytoloadcode = False
        self.readytorun = False
        self.enabled = False
        self.enabledisablereason = "n/a"
        #
        self.eventlist = EventList()


    def do_enabledisable(self, flag_enable, reason, eventlist):
        """Set the disabled flag for the package.  If False than the code for the package will not be loaded and run."""
        alreadyenabled = self.enabled
        # change state
        self.enabled = flag_enable
        self.enabledisablereason = reason
        # do stuff on change of state
        if (alreadyenabled == flag_enable):
            # nothing to do, it's already where we want it
            pass
        elif (flag_enable):
            # we want to enable this package that is currently not enabled
            # ATTN: todo - do we want to OVERRIDE/IGNORE any settings that say to disable this package when we are told to explicitly enable it? I say yes.
            self.startup()
        elif (not flag_enable):
            # we want to disable this package that is currently enabled
            self.shutdown()
        return None



    def create_packageobject(self, packageobj_class):
        """Create an appropriate child package; subclasses will reimplement this to use their preferred child class."""
        obj = packageobj_class(self)
        return obj


    def load_infofile(self):
        """Load the info file (json data) for this package."""

        # init
        self.infodict = None
        self.readytoloadcode = False

        # read the json file and parse it into a dictionary
        self.infodict, failure = readfile_asjson(self.infofilepath, "Package info file")
        if (failure == None):
            # set readytoloadcode true since the json parsed properly
            self.readytoloadcode = True
        else:
            # failed; add the error message to our eventlist, and continue with this package marked as not useable
            self.eventlist.add(failure)
            # we could raise an exception immediately if we wanted from the failure
            if (True):
                raise ExceptionPlus(failure)



    def load_codemodule(self):
        """Import the codemodule associated with this package."""

        # init
        self.codemodule = None
        self.codemodule_path = ''
        self.packageobject = None
        self.readytorun = False

        if (not self.enabled):
            # it's disabled, do nothing
            return

        # get path to code module
        self.codemodule_path, failure = self.get_pathtocodemodule()
        if (failure == None):
            # ask package manager to load the import from the path
            self.codemodule, failure = self.packagemanager.loadimport(self.codemodule_path)

        if (failure == None):
            # if the import worked, instantiate the package object from it
            failure = self.instantiate_packageobject()

        if (failure == None):
            # success so mark it as ready to run
            self.readytorun = True
        else:
            # failed; add the error message to our eventlist, and continue with this package marked as not useable
            self.eventlist.add(failure)
            if (True):
                raise ExceptionPlus(failure)



    def get_pathtocodemodule(self):
        """The info file for the package should tell us what module file to import; we default to same name as info file but with .py"""

        # default module name
        path = self.infofilepath
        dir, fullname = os.path.split(path)
        name, ext = os.path.splitext(fullname)
        pathtocodemodule_default = name + '.py'
        # override with explicit
        pathtocodemodule = dir + '/' + self.get_infofile_property('codefile', pathtocodemodule_default)
        # return it
        return pathtocodemodule, None



    def instantiate_packageobject(self):
        """Assuming we have imported the dynamic package module, now create the package object that we invoke to do work"""

        # init
        self.packageobject = None

        # module loaded in memory?
        if (self.codemodule == None):
            return EFailure("No code module imported to instantiate package object from.")

        # object class defined in info dictionary?
        packageobject_classname = self.get_infofile_property("codeclass", None)
        if (packageobject_classname == None):
            return EFailure("Package info file is missing the 'codeclass' property which defines the class of the MewloPackage derived class in the package module.")

        # does it exist
        if (not packageobject_classname in dir(self.codemodule)):
            return EFailure("Package class '{0}' not found in package module '{1}'.".format(packageobject_classname, self.codemodule.__name__))

        # instantiate it
        try:
            packageobj_class = getattr(self.codemodule, packageobject_classname)
            packageobj = self.create_packageobject(packageobj_class)
        except:
            return EFailure("Package class object '{0}' was found in package module, but could not be instantiated.".format(packageobject_classname))

        # save it for use
        self.packageobject = packageobj
        # no failure returns None
        return None



    def get_infofile_property(self, propertyname, defaultval=None):
        """Lookup property in our info dict and return it, or defaultval if not found."""

        if (self.infodict == None):
            return defaultval
        if (propertyname in self.infodict):
            return self.infodict[propertyname]
        return defaultval



    def update_queue_check(self):
        """Update: check online for new version. ATTN: UNFINISHED."""
        pass

    def update_queue_download(self):
        """Update: download a downloaded new version. ATTN: UNFINISHED."""
        pass

    def update_queue_install(self):
        """Update: install a new version. ATTN: UNFINISHED."""
        pass



    def startup(self):
        """Do any startup stuff."""
        if (self.readytoloadcode):
            # load the code module
            self.load_codemodule()
            if (self.packageobject!=None):
                # now start it up
                self.packageobject.startup()

    def shutdown(self):
        """Do any shutdown stuff."""
        if (self.packageobject!=None):
            self.packageobject.shutdown()
            # and now release the packageobject payload to garbage collection
            self.packageobject = None



    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""

        outstr = " "*indent + "Package reporting in:\n"
        indent += 1
        #
        outstr += self.eventlist.dumps(indent)
        #
        outstr += " "*indent + "Enabled: " + str(self.enabled) + " ("+self.enabledisablereason+").\n"
        #
        outstr += " "*indent + "Info dictionary: " + self.infofilepath + ":\n"
        jsonstring = json.dumps(self.infodict, indent+1)
        outstr += " "*indent + " '" + jsonstring + "'\n"
        #
        outstr += " "*indent + "Code module file: " + self.codemodule_path + "\n"
        #
        outstr += " "*indent + "Code module: "
        outstr += str(self.codemodule) + "\n"
        #
        outstr += " "*indent + "Package object: "
        outstr += str(self.packageobject) + "\n"
        if (self.packageobject):
            outstr += self.packageobject.dumps(indent+1)
        #
        return outstr

