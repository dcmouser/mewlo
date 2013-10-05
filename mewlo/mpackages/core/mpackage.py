"""
mpackage.py
This file defines the classes that support mewlo package/extensions.
They are custom subclasses from the pkg classes.
"""


# mewlo imports
import mglobals

# helper imports
from helpers.pkg.packageobject import PackageObject
from helpers.pkg.packagemanager import PackageManager
from helpers.pkg.package import Package
from helpers.event.event import EventList, EError, EWarning, EDebug
from helpers.misc import get_value_from_dict





class MewloPackage(Package):
    """
    The MewloPackage class represents an mewlo "package" aka extension/plugin/addon/component.
    It is *not* the same as a Python "package".
    All code (both core builtin code and 3rd party extensions/plugins) is always in the form of a mewlo package.
    The MewloPackage class exposes author and version info about a package, supports online, version checking, database updating, dependency chains, etc.
    """

    def __init__(self, packagemanager, filepath):
        # parent constructor
        super(MewloPackage, self).__init__(packagemanager, filepath)

    def create_packageobject(self, packageobj_class):
        """Create an appropriate child package."""
        obj = packageobj_class(self)
        return obj









class MewloPackageManager(PackageManager):
    """The MewloPackageManager manages a collection of MewloPackages."""

    # class constants
    DefMewlo_Package_filepatternsuffix = 'mpackage'

    def __init__(self):
        # parent constructor
        super(MewloPackageManager, self).__init__()
        # set file pattern of mewlo package files
        self.set_filepatternsuffix(self.DefMewlo_Package_filepatternsuffix)
        # set setuptools entrypoint groupname
        self.set_setuptools_entrypoint_groupname('mewlo.packages')


    def create_package(self, filepath):
        """Create an appropriate child package."""
        return MewloPackage(self, filepath)

















class MewloPackageObject(PackageObject):
    """
    The MewloPackageObject class is the parent class for the actual 3rd party class that will be instantiated when a package is LOADED+ENABLED
    """

    def __init__(self, package):
        # parent constructor
        super(MewloPackageObject, self).__init__(package)


    def startup(self):
        # parent
        super(MewloPackageObject, self).startup()


    def prepare(self):
        # called by Mewlo system when it's ready for us to do any setup stuff
        self.packagesettings = mglobals.mewlosite().get_packagesettings()
        # parent
        return super(MewloPackageObject, self).prepare()


    def log_signalmessage(self, txt, receiverobject, id, message, request, source):
        # helper function to log a message related to a signal
        txtplus = txt + " ReceiverObject: "+str(receiverobject)+"; id: "+id+"; message: "+str(message)+"; source: "+str(source)+"; request: "+str(request)
        # display message onscreen?
        if (False):
            print txtplus
        # log it
        txtevent = EDebug("Debug logging signal message: " + txtplus, flag_loc=True)
        mglobals.mewlosite().logevent(txtevent, request)


    def log_event(self, event, request = None):
        mglobals.mewlosite().logevent(event, request)


    def get_databaseversion(self):
        dbversion = self.packagesettings.get_subvalue(self.get_settingkey(),'database_version')
        return dbversion






