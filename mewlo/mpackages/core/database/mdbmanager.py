"""
mdbmanager.py
This module contains Mewlo database manager class.
"""

# mewlo imports
import dbmodel_settings
from dbmanager_sqlalchemy import DatabaseManagerSqlAlchemy
from mewlo.mpackages.core.msettings import MewloSettings
import mewlo.mpackages.core.mglobals as mglobals

# library imports
import sqlalchemy
import sqlalchemy.orm



class MewloDatabaseManager(DatabaseManagerSqlAlchemy):
    """The MewloDatabaseManager supervises database support."""

    def __init__(self):
        # parent func
        super(MewloDatabaseManager, self).__init__()
        pass



    def startup(self, mewlosite, eventlist):
        self.mewlosite = mewlosite
        # parent func
        super(MewloDatabaseManager, self).startup()
        self.startup_database_stuff(eventlist)

    def shutdown(self):
        # parent func
        super(MewloDatabaseManager, self).shutdown()
        pass







    def startup_database_stuff(self, eventlist):
        # now core database objects
        mglobals.db().create_modelclass(self, dbmodel_settings.DbModel_Settings, MewloSettings.DEF_DBCLASSNAME_PackageSettings, MewloSettings.DEF_DBTABLENAME_PackageSettings)
        # ATTN: Test
        mglobals.db().create_modelclass(self, dbmodel_settings.DbModel_Settings, MewloSettings.DEF_DBCLASSNAME_MainSettings, MewloSettings.DEF_DBTABLENAME_MainSettings)







    def resolve(self, text):
        """Sometimes database engine configuration settings will use mewlo aliases like {$databasedirectory}, etc.  This resolves them."""
        return self.mewlosite.resolve(text)






    def register_modelclass(self, owner, modelclass):
        """Register a model class with component system and create database mapper stuff."""
        # map database fields for it
        self.map_modelclass(modelclass)
        # register it with the registry
        mglobals.mewlosite().registry.register_class(owner, modelclass)
        return None



    def map_modelclass(self, modelclass):
        """Map the model class to the database."""
        # first tell the class to define it's fields
        modelclass.definedb()
        # now get fields
        fieldlist = modelclass.get_fieldlist()
        #print "MAPPING MODELCLASS FOR "+modelclass.__name__+" fieldlist: "+str(fieldlist)
        # now convert the fields to sqlalchemy columns
        sqlalchemycolumns = self.convert_dbfields_to_sqlalchemy_columns(fieldlist)
        # ok now create an sqlalchemy Table object from columns
        dbtablename = modelclass.get_dbtablename()
        dbschemaname = modelclass.get_dbschemaname()
        sqlahelper = self.get_sqlahelper(dbschemaname)
        metadata = sqlahelper.getmake_metadata()
        # build table object and save it
        #print "Tablename for modelclass is '{0}'.".format(dbtablename)
        modeltable = sqlalchemy.Table(dbtablename, metadata, *sqlalchemycolumns)
        # store/cache some of the object references in the class itself
        modelclass.setclass_dbinfo(modeltable, sqlahelper, self)
        # now ask sqlalchemy to map the class and table together, the key part of using sqlalchemy ORM
        sqlalchemy.orm.mapper(modelclass, modeltable)
        # create table if it doesn't exist
        metadata.create_all()





    def convert_dbfields_to_sqlalchemy_columns(self, fields):
        """Given a list of our internal fields, build sqlalchemy columns."""
        columns = []
        for field in fields:
            columns.append(field.convert_to_sqlalchemy_column())
        return columns



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


