"""
dbmanager_sqlalchemy.py

This is our database helper module

"""


# mewlo imports

# helper imports
import dbmanager
from ..event.event import EFailure

# python imports


# library imports
import sqlalchemy
import sqlalchemy.orm




class DbmSqlAlchemyHelper(object):
    """Helper for DatabaseManagerSqlAlchemy that holds engine, metadata, session, connection, data."""
    def __init__(self, dbmanager, dbsettings):
        """constructor."""
        # save settings
        self.dbsettings = dbsettings
        # init
        self.dbmanager = dbmanager
        self.engine = None
        self.metadata = None
        self.connection = None
        self.session = None


    def getmake_engine(self):
        """Return self.engine or create it if None."""
        if (self.engine == None):
            # create it
            if ('url' in self.dbsettings):
                self.url = self.resolve(self.dbsettings['url'])
            else:
                raise EFailure("Could not get 'url' for about database connections.")
            # create it!
            self.engine = sqlalchemy.create_engine(self.url)
            self.metadata = sqlalchemy.MetaData()
            self.metadata.bind = self.engine
        return self.engine


    def getmake_connection(self):
        """Return self.connection or create it if None."""
        if (self.connection == None):
            self.connection = self.engine.connect()
        return self.connection


    def getmake_session(self):
        """Return self.session or create it if None."""
        if (self.session == None):
            self.session = sqlalchemy.orm.sessionmaker(bind=self.getmake_engine())
        return self.session

    def resolve(self, text):
        return self.dbmanager.resolve(text)












class DatabaseManagerSqlAlchemy(dbmanager.DatabaseManager):
    """Derived DatabaseManager class built for sqlalchemy."""

    def __init__(self):
        """constructor."""
        # call parent func
        super(DatabaseManagerSqlAlchemy,self).__init__()
        # init
        self.alchemyhelpers = {}



    def startup(self):
        # call parent func
        super(DatabaseManagerSqlAlchemy,self).startup()
        # create helpers
        for idname in self.databasesettings.keys():
            self.alchemyhelpers[idname] = DbmSqlAlchemyHelper(self, self.databasesettings[idname])


    def shutdown(self):
        # call parent func
        super(DatabaseManagerSqlAlchemy,self).shutdown()
        pass



    def get_sqlahelper(self, idname):
        """Lookup the DbmSqlAlchemyHelper object based on the id given, creating engine/session if its first time."""
        # if already in our collection, just return it
        if (idname in self.alchemyhelpers):
            self.alchemyhelpers[idname].ensurecreate()
            return self.alchemyhelpers[idname]
        # not there, so look for a default connection
        idname = 'default'
        if (idname in self.alchemyhelpers):
            return self.alchemyhelpers[idname]
        # no default found, throw an error
        raise "Error in get_sqlahelper({0}), sqlalchemy database wrapper get_sqlahelper failed to find.".format(idname)



    def testcreate(self, idname):
        """Test function."""
        sqlahelper = self.get_sqlahelper(idname)
        engine = sqlahelper.getmake_engine()
        connection = sqlahelper.getmake_connection()
        session = sqlahelper.getmake_session()
        print " engine: "+str(engine)
        print " connection: "+str(connection)
        print " session: "+str(session)


