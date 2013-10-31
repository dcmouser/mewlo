"""
mdbmanager.py
This module contains Mewlo database manager class.
"""

# mewlo imports
import mdbmodel_settings
from ..setting.msettings import MewloSettings
from ..user import muser



class MewloDatabaseManager(object):
    """The MewloDatabaseManager supervises database support."""

    def __init__(self):
        self.databasesettings = {}


    def startup(self, mewlosite, eventlist):
        self.mewlosite = mewlosite

    def shutdown(self):
        pass




    def startup_database_stuff(self, eventlist):
        """Setup some database classes.
        ATTN: We may want to move this elsewhere eventually.
        """
        # now core database objects
        newclass = self.create_derived_dbmodelclass(self, mdbmodel_settings.MewloDbModel_Settings, MewloSettings.DEF_DBCLASSNAME_PackageSettings, MewloSettings.DEF_DBTABLENAME_PackageSettings)
        self.register_modelclass(self, newclass)

        # ATTN: Again, we should probably move this stuff elsewhere
        newclass = self.create_derived_dbmodelclass(self, mdbmodel_settings.MewloDbModel_Settings, MewloSettings.DEF_DBCLASSNAME_MainSettings, MewloSettings.DEF_DBTABLENAME_MainSettings)
        self.register_modelclass(self, newclass)
        # more
        self.register_modelclass(self, muser.MewloUser)
        #self.create_derived_dbmodelclass(self, muser.MewloUser)


    def makedbtables(self):
        pass


    def set_databasesettings(self, databasesettings):
        """Simple accessor."""
        self.databasesettings = databasesettings
        #print "ATTN: DATABASE SETTINGS1 ARE: "+str(self.databasesettings)

















    def process_request_starts(self, request):
        """Do stuff before processing a request."""
        pass


    def process_request_ends(self, request):
        """Do stuff before processing a request."""
        self.flushdb_on_request_ends()





    def flushdb_on_request_ends(self):
        """Nothing to do in base class."""
        pass

















    def resolve(self, text):
        """Sometimes database engine configuration settings will use mewlo aliases like {$databasedirectory}, etc.  This resolves them."""
        return self.mewlosite.resolve(text)














    def create_derived_dbmodelclass(self, owner, baseclass, classname=None, tablename=None, schemaname='default'):
        """
        Create a new *CLASS* based on another model class, with a custom classname and tablename.
        We only need to use this when we want to dynamically create multiple tables based from the same base model class.
        """
        # create the new class
        if (classname==None):
            targetclass = baseclass
        else:
            #print "Creating class {0} from class {1}.".format(classname,baseclass.__name__)
            targetclass = type(classname, (baseclass,),{})
        # tablename
        if (tablename==None):
            tablename=targetclass.__name__
        # set table info
        targetclass.set_dbnames(tablename, schemaname)

        # NOTE: it's not registered yet!

        # and return it
        return targetclass


    def register_modelclass(self, owner, modelclass):
        """Register a model class with component system and create database mapper stuff."""
        # map database fields for it
        self.map_modelclass(modelclass)
        # register it with the registry
        self.mewlosite.registry.register_class(owner, modelclass)
        return None



    def map_modelclass(self, modelclass):
        """Map the model class to the database; this is a derived function that subclass will implement."""
        pass











    def dumps(self, indent=0):
        """Debug information."""
        outstr = " "*indent + "DatabaseManager (" + self.__class__.__name__  + ") reporting in.\n"
        outstr += " "*indent + " Settings: "+str(self.databasesettings)
        return outstr
