"""
mdbmanager.py
This module contains Mewlo database manager class.
"""

# mewlo imports
from dbmanager_sqlalchemy import DatabaseManagerSqlAlchemy
import mewlo.mpackages.core.mglobals as mglobals


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






    def register_modelclass(self, owner, modelclass):
        """Register a model class with component system and create database mapper stuff."""
        # map database fields for it
        self.map_modelclass(modelclass)
        # register it with the registry
        mglobals.mewlosite().registry.register_class(owner, modelclass)
        return None


    def map_modelclass(self, modelclass):
        """Map the model class to the database."""
        # ATTN: ToDo
        pass


    def resolvealias(self, text):
        """Sometimes database engine configuration settings will use mewlo aliases like {$databasedirectory}, etc.  This resolves them."""
        return mglobals.mewlosite().resolvealias(text)