"""
dbmanager_sqlalchemy.py

This is our database helper module

"""


# mewlo imports
# ATTN: THIS SHOULD NOT BE FOUND IN A HELPERS MODULE
import mewlo.mpackages.core.mglobals as mglobals

# helper imports
import dbmanager
from ..helpers.event.event import EFailure
from ..helpers.misc import get_value_from_dict


# python imports
import logging

# library imports
import sqlalchemy
import sqlalchemy.orm




class DbmSqlAlchemyHelper(object):
    """Helper for DatabaseManagerSqlAlchemy that holds engine, metadata, session, connection, data."""




    def __init__(self, dbmanager, dbsettings):
        """constructor."""
        # save settings
        self.dbsettings = dbsettings
        self.dbmanager = dbmanager
        # init
        self.engine = None
        self.metadata = None
        self.connection = None
        self.session = None

    def ensurecreate(self):
        """Do nothing?"""
        pass

    def getmake_metadata(self):
        """To make metadata we just call make engine."""
        if (self.metadata==None):
            tempengine = self.getmake_engine()
        return self.metadata


    def getmake_engine(self):
        """Return self.engine or create it if None."""
        if (self.engine == None):
            # create it
            if ('url' in self.dbsettings):
                self.url = self.resolve(self.dbsettings['url'])
            else:
                raise EFailure("Could not get 'url' for about database connections.")
            # logging flag?
            flag_echologging = get_value_from_dict(self.dbsettings, 'flag_echologging', True)
            # create it!
            self.engine = sqlalchemy.create_engine(self.url, echo=flag_echologging)
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
        if (self.session!=None):
            self.session.commit()
            self.session.close()
            self.session=None
        if (self.engine!=None):
            self.engine.dispose()
            self.engine=None
        if (self.connection!=None):
            self.connection.close()
            self.connection=None









class DatabaseManagerSqlAlchemy(dbmanager.DatabaseManager):
    """Derived DatabaseManager class built for sqlalchemy."""

    # class vars
    DEF_SqlAlchemyLoggerName = 'sqlalchemy'


    def __init__(self):
        """constructor."""
        # call parent func
        super(DatabaseManagerSqlAlchemy,self).__init__()
        # init
        # helpers for different databases
        self.alchemyhelpers = {}
        self.sqlalchemylogger = None
        self.sqlalchemy_loglevel = logging.NOTSET



    def startup(self):
        # call parent func
        super(DatabaseManagerSqlAlchemy,self).startup()
        # create helpers
        for idname in self.databasesettings.keys():
            self.alchemyhelpers[idname] = DbmSqlAlchemyHelper(self, self.databasesettings[idname])
        # settings
        self.sqlalchemy_loglevel = get_value_from_dict(self.databasesettings['settings'],'sqlalchemy_loglevel',logging.DEBUG)
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
        # ATTN:TODO - find a way to not have to call a MEWLO thing here, since we are in helper directory and supposed to be independent of mewlo here
        self.sqlalchemylogger = mglobals.mewlosite().logmanager.hook_pythonlogger(DatabaseManagerSqlAlchemy.DEF_SqlAlchemyLoggerName, self.sqlalchemy_loglevel)





    def set_sqlalchemydebuglevel(self, level):
        """Helper to set debugging level of sql alchemy."""
        # ok get/create the logger, and set its log level
        self.sqlalchemylogger.setLevel(level)


    def sqlalchemydebuglevel_temporarydisable(self):
        """Helper to set debugging level of sql alchemy."""
        self.set_sqlalchemydebuglevel(logging.NOTSET)

    def sqlalchemydebuglevel_donetemporarydisable(self):
        """Helper to set debugging level of sql alchemy."""
        self.set_sqlalchemydebuglevel(self.sqlalchemy_loglevel)

















    def get_modelclass_dbsession(self, modelclass):
        """Shortcut to get info from class object."""
        sqlahelper = modelclass.dbsqlahelper
        return sqlahelper.getmake_session()













    # Real-work database functions





    def model_add(self, modelobj):
        """Add the model object."""
        session = modelobj.dbsession()
        session.add(modelobj)
        # doing a commit after every operation is a HUGE slowdown
        #session.commit()
        return None


    def model_update(self, modelobj):
        """Update the model object -- for sqlalchemy this is same as add()?"""
        # ATTN: Check into the session merge() function.
        return self.model_add(modelobj)


    def model_delete(self, modelobj):
        """Delete the model object."""
        session = modelobj.dbsession()
        session.delete(modelobj)
        # doing a commit after every operation is a HUGE slowdown
        #session.commit()
        return None



    def modelclass_deleteall(self, modelclass):
        """Delete all items (rows) in the table."""
        # ATTN: Unfinished
        pass


    def modelclass_delete_bykey(self, modelclass, keydict):
        """Delete all items (rows) matching key dictionary settings."""
        # ATTN: Unfinished
        pass



    def modelclass_find_one_bykey(self, modelclass, keydict, defaultval):
        """Find and return an instance object for the single row specified by keydict.
        :return: defaultval if not found
        """
        session = modelclass.dbsession()
        query = session.query(modelclass).filter_by(**keydict)
        result = query.first()
        if (result!=None):
            return result
        return defaultval


    def modelclass_find_all(self, modelclass):
        """Load *all* rows and return them as array."""
        session = self.get_modelclass_dbsession(modelclass)
        query = session.query(modelclass)
        result = query.all()
        return result

