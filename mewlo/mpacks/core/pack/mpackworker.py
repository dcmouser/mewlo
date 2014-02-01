"""
mpackpaypload.py
Works with mpackmanager.py and mpack.py to support our pack/extension/addon system
"""


# mewlo imports
from ..eventlog.mevent import EFailure, EDebug


class MewloPackWorker(object):
    """
    The PackWorker class is the parent class for the actual 3rd party class that will be instantiated when a pack is LOADED+ENABLED.
    """

    def __init__(self, pack):
        self.pack = pack
        # default name
        self.settingkey = self.__class__.__name__


    def get_settingkey(self):
        return self.settingkey


    def prepare(self, packsettings):
        # called by Mewlo system when it's ready for us to do any setup stuff
        self.packsettings = packsettings

    def get_mewlosite(self):
        return self.pack.get_mewlosite()

    def startup(self, mewlosite, eventlist):
        """Do any startup stuff."""
        return None

    def shutdown(self):
        """Do any shutdown stuff."""
        # here we want to unregister any signals and components
        self.get_mewlosite().comp('registrymanager').unregister_byowner(self)
        self.get_mewlosite().comp('signalmanager').unregister_byowner(self)
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
        This is a helper function that a pack can use to persistently set (in database) the version of the current database tables in use by the pack.
        This is a key feature that allows a pack to tell when it needs to update its database tables, and to ensure consistency between code version and database changes between versions.
        The database_version is a string, typically of format ##.##.##
        """
        return self.packsettings.get_subvalue(self.get_settingkey(),'database_version')



    def set_databaseversion(self, val):
        """
        This is a helper function that a pack can use to persistently set (in database) the version of the current database tables in use by the pack.
        This is a key feature that allows a pack to tell when it needs to update its database tables, and to ensure consistency between code version and database changes between versions.
        The database_version is a string, typically of format ##.##.##
        """
        self.packsettings.set_subvalue(self.get_settingkey(),'database_version',val)















    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = " "*indent + "Base PackWorker reporting in.\n"
        return outstr



























    def updatecheck_checkdatabase(self):
        """
        This function should be implemented by derived classes.
        Check if this pack object needs to run a database update before it can be used.
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
        Check if this pack object is actually able to run, before startup is called.
        :return: None if all is good and its runable, or failure event if not.
        Note that elsewhere are performed checks according to whether the pack info file specifies pre-requisite required co-packd are met and enabled.
        Note that elsewhere we check if the database needs an update.
        So this function is just for more specific tests beyond those.
        :return: failure (or None on success)
        """
        return None


