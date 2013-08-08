"""
package.py
Works with packagemanager.py to support our package/extension/addon system
"""



# python libraries
import json
import os

# mewlo stuff
from mewlo.mpackages.core.helpers.eventtracker import EventTracker




class Package(object):
    """
    The Package is a class represents a dynamically found module that can be used as an addon package.
    """

    def __init__(self, packagemanager, filepath):
        # keep pointer to package manager
        self.packagemanager = packagemanager
        # found info (json) file defining the package
        self.infofilepath = filepath
        # dictionary acquired from info file
        self.infodict = None
        # imported module of code
        self.codemodule_path = ""
        self.codemodule = None
        self.packageobject = None
        # last error, for debug display
        self.readytoloadcode = False
        self.readytorun = False
        self.enabled = False
        self.eventtracker = EventTracker()



    def adderror(self, errorstr):
        """Add an error string to our error tracker."""
        if (errorstr!=""):
            self.eventtracker.error(errorstr)



    def load_infofile(self):
        """Load the info file for this package."""
        # init
        self.infodict = None
        self.readytoloadcode = False
        errorstr = ""
        file = None
        # load the file into a string
        try:
            jsonstr = ""
            # make sure filename is nonblanck
            if (self.infofilepath == ""):
                raise Exception("package has blank info file path")
            # open file for reading, and read it into string
            file = open(self.infofilepath,"r")
            if (file):
                # read the file
                jsonstr = file.read()
                # parse string as json
                try:
                    self.infodict = json.loads(jsonstr)
                except Exception as exp:
                    errorstr = "Failure to parse package info (json) file ("+self.infofilepath+"): "+str(exp)
            else:
                errorstr="Failed to open package info (json) file ("+self.infofilepath+")."
        except Exception as exp:
            errorstr = "Failure to open and read package info file ("+self.infofilepath+"): "+str(exp)
        finally:
            if (file):
                file.close()

        # record error
        self.adderror(errorstr)

        # set readytoloadcode if the json parsed properly
        if (errorstr==""):
            self.readytoloadcode = True

        # return it
        return (self.infodict,errorstr)



    def load_codemodule(self):
        """Import the codemodule associated with this package."""

        # init
        self.codemodule = None
        self.codemodule_path = ""
        self.packageobject = None
        self.readytorun = False
        self.enabled = False
        errorstr = ""

        # get path to code module
        self.codemodule_path = self.get_pathtocodemodule()

        # ask package manager to load the import from the path
        (self.codemodule,errorstr) = self.packagemanager.loadimport(self.codemodule_path)

        # if the import worked, instantiate the package object from it
        if (errorstr==""):
            errorstr = self.instantiate_packageobject()

        # if no error, we are ready to run, and default to enabled
        if (errorstr==""):
            self.readytorun = True
            self.enabled = True

        # record error
        self.adderror(errorstr)

        # return it
        return (self.codemodule,errorstr)



    def get_pathtocodemodule(self):
        """The info file for the package should tell us what module file to import; we default to same name as info file but with .py"""
        # default module name
        path = self.infofilepath
        dir, fullname = os.path.split(path)
        name, ext = os.path.splitext(fullname)
        pathtocodemodule_default = name + ".py"
        # override with explicit
        pathtocodemodule = dir + "/" + self.get_infofile_property("codefile",pathtocodemodule_default)
        # return it
        return pathtocodemodule



    def instantiate_packageobject(self):
        """Assuming we have imported the dynamic package module, now create the package object that we invoke to do work"""
        # init
        errorstr = ""
        packageobj = None
        # module loaded in memory?
        if (self.codemodule == None):
            return "No code module imported to instantiate package object from"
        # object class defined in info dictionary?
        packageobject_classname = self.get_infofile_property("codeclass","_")
        if (packageobject_classname == "_"):
            return "Package info file is missing the 'codeclass' property which defines the class of the MewloPackage derived class in the package module"
        # does it exist
        if (not packageobject_classname in dir(self.codemodule)):
            return "Package class ("+packageobject_classname+") not found in package module"
        # instantiate it
        try:
            packageobj_class = getattr(self.codemodule, packageobject_classname)
            packageobj = packageobj_class(self)
        except:
            return "Package class object ("+packageobject_classname+") was found in package module, but could not be instantiated; STACK TRACEBACK: "+traceback.format_exc()
        # save it for use
        self.packageobject = packageobj
        # success
        return ""



    def get_infofile_property(self, propertyname, defaultval):
        """Lookup property in our info dict and return it, or defaultval if not found."""
        if (self.infodict==None):
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



    def debug(self,indentstr=""):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = indentstr+"Package reporting in.\n"
        indentstr += " "
        #
        outstr += self.eventtracker.debug(indentstr)+"\n"
        #
        outstr += indentstr+"Info dictionary ("+self.infofilepath+"):\n"
        jsonstring = json.dumps(self.infodict, indent=12)
        outstr += indentstr+" '"+jsonstring+"'\n"
        #
        outstr += indentstr+"Code Module file: "+self.codemodule_path+"\n"
        #
        outstr += indentstr+"Code module: "
        outstr += str(self.codemodule)+"\n"
        #
        outstr += indentstr+"Package object: "
        outstr += str(self.packageobject)+"\n"
        if (self.packageobject):
            outstr += self.packageobject.debug(indentstr+" ")
        #
        return outstr

