"""
mdbmanager.py
This module contains Mewlo database manager class.
"""

# mewlo imports
from dbmanager_sqlalchemy import DatabaseManagerSqlAlchemy
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



    def startup(self, eventlist):
        # parent func
        super(MewloDatabaseManager, self).startup()
        pass

    def shutdown(self):
        # parent func
        super(MewloDatabaseManager, self).shutdown()
        pass







    def resolvealias(self, text):
        """Sometimes database engine configuration settings will use mewlo aliases like {$databasedirectory}, etc.  This resolves them."""
        return mglobals.mewlosite().resolvealias(text)






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
        fields = modelclass.get_fields()
        # now convert the fields to sqlalchemy columns
        sqlalchemycolumns = self.convert_dbfields_to_sqlalchemy_columns(fields)
        # ok now create an sqlalchemy Table object from columns
        dbtablename = modelclass.get_dbtablename()
        dbschemaname = modelclass.get_dbschemaname()
        sqlahelper = self.get_sqlahelper(dbschemaname)
        metadata = sqlahelper.getmake_metadata()
        # build table object and save it
        modeltable = sqlalchemy.Table(dbtablename, metadata, *sqlalchemycolumns)
        # store/cache some of the object references in the class itself
        modelclass.store_dbdata(modeltable, sqlahelper, self)
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
        newclass = type(classname, (baseclass,),{})
        # set table info
        newclass.set_dbnames(tablename, schemaname)
        # now register it
        self.register_modelclass(owner,newclass)
        # and return it
        return newclass


