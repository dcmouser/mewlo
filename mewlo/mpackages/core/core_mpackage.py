"""
core_mpackage.py
This file "manages" the core Mewlo classes.

By "manage" we mean the following:

All code in mewlo, both the core code, and any 3rd party addons/plugins/extensions, is considered to be "managed" by a MewloPackage.
The MewloPackage provides information about the version of the code release and associated information suitable for doing online update checking,
 as well as author information, and dependency information between packages, etc.

So this Core_MewloPackageObject is the "manager" or owner of all core mewlo code.
It doesn't actually *do* anything -- but does describe and version the core code.

"""



# mewlo imports
import mpackage
import mglobals
import database.dbmodel_settingsdict as dbmodel_settingsdict




class Core_MewloPackageObject(mpackage.MewloPackageObject):
    """
    The Core_MewloPackage class manages the core mewlo code
    """

    def __init__(self, package):
        # parent constructor
        super(Core_MewloPackageObject, self).__init__(package)


    def startup(self):
        # called by Mewlo system when it's ready for us to do any setup stuff
        # return failure if any, or None on success
        retv = self.setup_everything()
        if (retv != None):
            return retv
        #
        return None


    def shutdown(self):
        # called by Mewlo system when it's ready for us to do any shutdown
        super(Core_MewloPackageObject, self).shutdown()
        return None





    def setup_everything(self):
        # called by Mewlo system when it's ready for us to do any setup stuff
        # let's register database classes
        ##self.setup_databaseclasses()
        return None




    def setup_databaseclasses(self):
        # called by Mewlo system when it's ready for us to do any setup stuff
        # let's register database classes
        # test
        #retv = mglobals.db().register_modelclass(self, dbmodel_settingsdict.DbModel_SettingsDictionary)
        return None





    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        str = " "*indent + "Core_MewloPackageObject reporting in.\n"
        return str

