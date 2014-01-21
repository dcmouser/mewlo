"""
mpackagepbject.py
Works with mpackagemanager.py and mpackage.py to support our package/extension/addon system
"""


# mewlo imports
from ..eventlog.mevent import EFailure, EDebug


class MewloPackageObject(object):
    """
    The PackageObject class is the parent class for the actual 3rd party class that will be instantiated when a package is LOADED+ENABLED.
    """

    def __init__(self, package):
        self.package = package
        # default name
        self.settingkey = self.__class__.__name__


    def get_settingkey(self):
        return self.settingkey


    def prepare(self, packagesettings):
        # called by Mewlo system when it's ready for us to do any setup stuff
        self.packagesettings = packagesettings

    def get_mewlosite(self):
        return self.package.get_mewlosite()

    def startup(self, mewlosite, eventlist):
        """Do any startup stuff."""
        return None

    def shutdown(self):
        """Do any shutdown stuff."""
        # here we want to unregister any signals and components
        self.get_mewlosite().registry.unregister_byowner(self)
        self.get_mewlosite().dispatcher.unregister_byowner(self)
        return None



















    def log_signalmessage(self, txt, receiverobject, id, message, request, source):
        """Just a shortcut function to log a message related to a signal."""
        txtplus = txt + " ReceiverObject: "+str(receiverobject)+"; id: "+id+"; message: "+str(message)+"; source: "+str(source)+"; request: "+str(request)
        # display message onscreen?
        if (False):
            print txtplus
        # log it
        txtevent = EDebug("Debug logging signal message: " + txtplus, flag_loc=True)
        self.get_mewlosite().logevent(txtevent, request)


    def log_event(self, event, request = None):
        """Just a shortcut function to ask our mewlosite to log an event for us."""
        self.get_mewlosite().logevent(event, request)
















    def get_databaseversion(self):
        """
        This is a helper function that a package can use to persistently set (in database) the version of the current database tables in use by the package.
        This is a key feature that allows a package to tell when it needs to update its database tables, and to ensure consistency between code version and database changes between versions.
        The database_version is a string, typically of format ##.##.##
        """
        return self.packagesettings.get_subvalue(self.get_settingkey(),'database_version')



    def set_databaseversion(self, val):
        """
        This is a helper function that a package can use to persistently set (in database) the version of the current database tables in use by the package.
        This is a key feature that allows a package to tell when it needs to update its database tables, and to ensure consistency between code version and database changes between versions.
        The database_version is a string, typically of format ##.##.##
        """
        self.packagesettings.set_subvalue(self.get_settingkey(),'database_version',val)















    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = " "*indent + "Base PackageObject reporting in.\n"
        return outstr



























    def updatecheck_checkdatabase(self):
        """
        This function should be implemented by derived classes.
        Check if this package object needs to run a database update before it can be used.
        :return: tuple (isdatabaseupdateneeded, failure)
        """
        return False, None




    def updaterun_database(self):
        """
        This function should be implemented by derived classes.
        Run a database update.
        :return: tuple (didupdate, failure)
        """
        return False, None









    def check_isusable(self):
        """
        This function should be implemented by derived classes.
        Check if this package object is actually able to run, before startup is called.
        :return: None if all is good and its runable, or failure event if not.
        Note that elsewhere are performed checks according to whether the package info file specifies pre-requisite required co-packaged are met and enabled.
        Note that elsewhere we check if the database needs an update.
        So this function is just for more specific tests beyond those.
        :return: failure (or None on success)
        """
        return None


