"""
mdbmanager.py
This module contains Mewlo database manager class.
"""

from helpers.database.dbmanager_sqlalchemy import DatabaseManagerSqlAlchemy


import mglobals


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




    def resolve(self, text):
        return mglobals.mewlosite().resolvealias(text)