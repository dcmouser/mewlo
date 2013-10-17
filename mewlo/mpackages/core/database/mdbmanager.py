"""
mdbmanager.py
This module contains Mewlo database manager class.
"""

# mewlo imports
import mdbmodel_settings
from ..setting.msettings import MewloSettings




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
        self.create_modelclass(self, mdbmodel_settings.MewloDbModel_Settings, MewloSettings.DEF_DBCLASSNAME_PackageSettings, MewloSettings.DEF_DBTABLENAME_PackageSettings)
        # ATTN: Test
        self.create_modelclass(self, mdbmodel_settings.MewloDbModel_Settings, MewloSettings.DEF_DBCLASSNAME_MainSettings, MewloSettings.DEF_DBTABLENAME_MainSettings)




    def set_databasesettings(self, databasesettings):
        """Simple accessor."""
        self.databasesettings = databasesettings
        print "ATTN: DATABASE SETTINGS1 ARE: "+str(self.databasesettings)




    def resolve(self, text):
        """Sometimes database engine configuration settings will use mewlo aliases like {$databasedirectory}, etc.  This resolves them."""
        return self.mewlosite.resolve(text)














    def create_modelclass(self, owner, baseclass, classname, tablename, schemaname='default'):
        """Create a new *CLASS* based on another model class, with a custom classname and tablename."""
        # create the new class
        if (classname==None):
            targetclass = baseclass
        else:
            #print "Creating class {0} from class {1}.".format(classname,baseclass.__name__)
            targetclass = type(classname, (baseclass,),{})
        # set table info
        targetclass.set_dbnames(tablename, schemaname)
        # now register it
        self.register_modelclass(owner, targetclass)
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
