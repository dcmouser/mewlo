"""
dbmanager_sqlalchemy.py

This is our database helper module

"""


# helper imports
import mdbmanager
from ..eventlog.mevent import EFailure
from ..helpers.misc import get_value_from_dict

# python imports
import logging

# library imports
import sqlalchemy
import sqlalchemy.orm







class DbmSqlAlchemyHelper(object):
    """
    Helper for MewloDatabaseManagerSqlA that holds engine, metadata, session, connection, data.
    We can have multiple DbmSqlAlchemyHelper's, so that some models can be using some databases, and some using others.
    We use the concept of 'schema' to group models with different database setups (DbmSqlAlchemyHelper's).
    Each model class also caches a reference to the DbmSqlAlchemyHelper that manages the class.
    """


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
        #
        sqlalchemy.orm.clear_mappers()


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


    def makedbtable(self):
        # create table if it doesn't exist
        if (self.metadata!=None):
            self.dbcommit()
            self.metadata.create_all()



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



    def dbflush(self):
        """Flush db if appropriate (less than commit)."""
        # see http://stackoverflow.com/questions/4201455/sqlalchemy-whats-the-difference-between-flush-and-commit
        if (self.session!=None):
            self.session.flush()

    def dbcommit(self):
        """Flush and commit db if appropriate.
        sqlalchemy does flush as part of commit.
        """
        # see http://stackoverflow.com/questions/4201455/sqlalchemy-whats-the-difference-between-flush-and-commit
        if (self.session!=None):
            self.session.commit()











class MewloDatabaseManagerSqlA(mdbmanager.MewloDatabaseManager):
    """Derived DatabaseManager class built for sqlalchemy."""

    # class vars
    DEF_SqlAlchemyLoggerName = 'sqlalchemy'


    def __init__(self):
        """constructor."""
        # call parent func
        super(MewloDatabaseManagerSqlA,self).__init__()
        # init
        # helpers for different databases
        self.alchemyhelpers = {}
        self.sqlalchemylogger = None
        self.sqlalchemy_loglevel = logging.NOTSET



    def startup(self, mewlosite, eventlist):
        # call parent func
        super(MewloDatabaseManagerSqlA,self).startup(mewlosite, eventlist)
        # create helpers
        #print "ATTN: DATABASE SETTINGS2 ARE: "+str(self.databasesettings)
        for key,val in self.databasesettings.iteritems():
            self.alchemyhelpers[key] = DbmSqlAlchemyHelper(self, val)
        # settings
        self.sqlalchemy_loglevel = get_value_from_dict(self.databasesettings['settings'],'sqlalchemy_loglevel',logging.DEBUG)
        # let's put in place some log catchers
        self.setup_logcatchers()


    def shutdown(self):
        # call parent func
        super(MewloDatabaseManagerSqlA,self).shutdown()
        # shutdown helpers
        for key,val in self.alchemyhelpers.iteritems():
            val.shutdown()








    def UNUSED_flushdb_on_request_ends(self):
        """Flush any sessions."""
        self.flush_all_dbs()

    def commitdb_on_request_ends(self):
        """Flush any sessions."""
        self.commit_all_dbs()



    def UNUSED_flush_all_dbs(self):
        """Ask all helpers to flush."""
        #print "DEBUG: FLUSHING DBs"
        for key,val in self.alchemyhelpers.iteritems():
            val.dbflush()

    def commit_all_dbs(self):
        """Ask all helpers to flush."""
        #print "DEBUG: FLUSHING DBs"
        for key,val in self.alchemyhelpers.iteritems():
            val.dbcommit()











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
        raise Exception("Error in get_sqlahelper -- sqlalchemy database wrapper get_sqlahelper failed to find for id '{0}'.".format(idname))



    def setup_logcatchers(self):
        """Catch sqlalchemy log statements and route to Mewlo."""
        # ATTN:TODO - find a way to not have to call a MEWLO thing here, since we are in helper directory and supposed to be independent of mewlo here
        self.sqlalchemylogger = self.mewlosite.logmanager.hook_pythonlogger(MewloDatabaseManagerSqlA.DEF_SqlAlchemyLoggerName, self.sqlalchemy_loglevel)





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


    def model_sessionflush(self, modelobj):
        """Flush the session associated with model."""
        session = modelobj.dbsession()
        session.flush()


    def modelclass_deleteall(self, modelclass):
        """Delete all items (rows) in the table."""
        # ATTN: Unfinished
        pass


    def modelclass_delete_bykey(self, modelclass, keydict):
        """Delete all items (rows) matching key dictionary settings."""
        # ATTN: Unfinished
        pass



    def modelclass_find_one_byprimaryid(self, modelclass, primaryid, defaultval):
        """Find and return an instance object for the single row specified by keydict.
        :return: defaultval if not found
        """
        session = modelclass.dbsession()
        result = session.query(modelclass).get(primaryid)
        if (result!=None):
            return result
        return defaultval


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





















    def makedbtables(self):
        """
        Ask sqlalchemy to build the actual tables for the models that have been created so-far.
        NOTE: we may call this more than once; once initially for some early models we need, and then later after startup completes.
        """
        for key,val in self.alchemyhelpers.iteritems():
            val.makedbtable()









