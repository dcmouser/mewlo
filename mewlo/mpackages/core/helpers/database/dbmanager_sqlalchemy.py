"""
dbmanager_sqlalchemy.py

This is our database helper module

"""


# mewlo imports
# ATTN: THIS SHOULD NOT BE FOUND IN A HELPERS MODULE
import mewlo.mpackages.core.mglobals as mglobals

# helper imports
import dbmanager
from ..event.event import EFailure
from ..misc import get_value_from_dict


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
            # logging flag?
            flag_enablelogging = get_value_from_dict(self.dbsettings, 'flag_enablelogging', True)
            # create it!
            self.engine = sqlalchemy.create_engine(self.url, echo=flag_enablelogging)
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
            Session = sqlalchemy.orm.sessionmaker(bind=self.getmake_engine())
            self.session = Session()
        return self.session

    def resolve(self, text):
        return self.dbmanager.resolve(text)


    def shutdown(self):
        """Shutdown any sqlalchemy stuff."""
        if (self.engine!=None):
            self.engine.dispose()
            self.engine=None
        if (self.session!=None):
            self.session.close()
            self.session=None
        if (self.connection!=None):
            self.connection.close()
            self.connection=None









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
        # let's put in place some log catchers
        self.setup_logcatchers()

    def shutdown(self):
        # call parent func
        super(DatabaseManagerSqlAlchemy,self).shutdown()
        # shutdown helpers
        for idname in self.alchemyhelpers.keys():
            self.alchemyhelpers[idname].shutdown()



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



    def setup_logcatchers(self):
        """Catch sqlalchemy log statements and route to Mewlo."""
        mglobals.mewlosite().logmanager.hook_pythonlogger('sqlalchemy')





    def dbtest(self, idname):
        """Test function."""
        sqlahelper = self.get_sqlahelper(idname)
        engine = sqlahelper.getmake_engine()
        connection = sqlahelper.getmake_connection()
        session = sqlahelper.getmake_session()
        #print " engine: "+str(engine)
        #print " connection: "+str(connection)
        #print " session: "+str(session)


