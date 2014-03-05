"""
dbmanager_sqlalchemy.py

This is our database helper module

"""


# mewlo imports
import mdbmanager
from ..eventlog.mevent import EFailure
from ..helpers.misc import get_value_from_dict
from ..constants.mconstants import MewloConstants as mconst

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


    def sqlahelper_makedbtables_all(self):
        # create any tables that don't exit
        if (self.metadata!=None):
            self.dbcommit()
            self.metadata.create_all()

    def sqlahelper_makedbtable_one(self, tablename):
        # create one table if it doesn't exist
        if (self.metadata!=None):
            self.dbcommit()
            self.metadata.create_all(tables=[tablename])





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



    def __init__(self, mewlosite, debugmode):
        """constructor."""
        # call parent func
        super(MewloDatabaseManagerSqlA,self).__init__(mewlosite, debugmode)
        # init
        # helpers for different databases
        self.alchemyhelpers = {}
        self.sqlalchemylogger = None
        self.sqlalchemy_loglevel = logging.NOTSET



    def prestartup_register(self, eventlist):
        """Called before starting up, to ask managers to register any database classes BEFORE they may be used in startup."""
        super(MewloDatabaseManagerSqlA,self).prestartup_register(eventlist)
        # this needs to be done at this state so it's ready for database table creation, etc.
        self.setup_sqlahelpers(eventlist)

    def setup_sqlahelpers(self, eventlist):
        # create helpers
        # print "ATTN: DATABASE SETTINGS2 ARE: "+str(self.databasesettings)
        for key,val in self.databasesettings.iteritems():
            self.alchemyhelpers[key] = DbmSqlAlchemyHelper(self, val)
        # settings
        self.sqlalchemy_loglevel = get_value_from_dict(self.databasesettings['settings'],'sqlalchemy_loglevel',logging.DEBUG)
        # let's put in place some log catchers
        self.setup_logcatchers()


    def startup(self, eventlist):
        # call parent func
        super(MewloDatabaseManagerSqlA,self).startup(eventlist)








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
        self.sqlalchemylogger = self.mewlosite.comp('logmanager').hook_pythonlogger(mconst.DEF_LOG_SqlAlchemyLoggerName, self.sqlalchemy_loglevel)





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




    def model_save(self, modelobj):
        """Save the model object."""
        session = modelobj.dbsession()
        session.add(modelobj)
        # doing a commit after every operation is a HUGE slowdown
        #session.commit()
        return None


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
        raise Exception("mdbmanager.modelclass_deleteall Not implemented yet.")


    def modelclass_delete_bykey(self, modelclass, keydict):
        """Delete all items (rows) matching key dictionary settings."""
        session = modelclass.dbsession()
        query = session.query(modelclass).filter_by(**keydict)
        result = query.delete()
        return result



    def modelclass_find_one_byprimaryid(self, modelclass, primaryid, defaultval=None):
        """Find and return an instance object for the single row specified by keydict.
        :return: defaultval if not found
        """
        session = modelclass.dbsession()
        result = session.query(modelclass).get(primaryid)
        if (result!=None):
            return result
        return defaultval


    def modelclass_find_one_bykey(self, modelclass, keydict, defaultval=None):
        """Find and return an instance object for the single row specified by keydict.
        :return: defaultval if not found
        """
        session = modelclass.dbsession()
        query = session.query(modelclass).filter_by(**keydict)
        result = query.first()
        if (result!=None):
            return result
        return defaultval

    def modelclass_find_all_bykey(self, modelclass, keydict, defaultval=None):
        """Find and return an instance object for the single row specified by keydict.
        :return: defaultval if not found
        """
        session = modelclass.dbsession()
        query = session.query(modelclass).filter_by(**keydict)
        result = query.all()
        return result



    def modelclass_find_all_bykey_within(self, modelclass, keydict, defaultval=None):
        """Find and return an instance object for the single row specified by keydict.
        :return: defaultval if not found
        """
        session = modelclass.dbsession()

        # the keydict MIGHT specify a LIST for each dictionary value
        query = session.query(modelclass)
        for (key,val) in keydict.iteritems():
            if (hasattr(val,'__iter__')):
                if (len(val)==0):
                    query = query.filter_by({key:None})
                elif (len(val)==10):
                    query = query.filter_by({key:val[0]})
                else:
                    # build sql filterstring from list
                    querystr = self.build_filter_from_inlist(key,val)
                    print "QUERYSTR = '{0}'.".format(querystr)
                    query = query.filter(querystr)
            else:
                query = query.filter_by({key:val})

        result = query.all()
        return result



    def build_filter_from_inlist(self, key, val):
        """Build a filter when we have a list."""
        strlist = []
        for v in val:
            if (v==None):
                strlist.append("NULL")
            else:
                strlist.append(str(v))
        querystr = '{0} in ({1})'.format(key, ",".join(strlist))
        return querystr


    def modelclass_find_all(self, modelclass):
        """Load *all* rows and return them as array."""
        session = self.get_modelclass_dbsession(modelclass)
        query = session.query(modelclass)
        result = query.all()
        return result





    def modelclass_find_one_bywhereclause(self, modelclass, whereclause, defaultval=None):
        """Find using a where clause."""
        whereclause = self.convertwhereclause(whereclause)
        session = modelclass.dbsession()
        query = session.query(modelclass).filter(whereclause)
        result = query.first()
        if (result!=None):
            return result
        return defaultval


    def modelclass_delete_all_bywhereclause(self, modelclass, whereclause):
        """Delete all using using a where clause."""
        whereclause = self.convertwhereclause(whereclause)
        session = modelclass.dbsession()
        query = session.query(modelclass).filter(whereclause)
        result = query.delete(synchronize_session=False)
        return result


    def modelclass_update_all_dict_bywhereclause(self, modelclass, updatedict, whereclause):
        """Update all with dictionary using a where clause."""
        whereclause = self.convertwhereclause(whereclause)
        session = modelclass.dbsession()
        query = session.query(modelclass).filter(whereclause)
        result = query.update(updatedict, synchronize_session=False)




    def convertwhereclause(self, whereclause):
        """Convert to a text clause if it's text."""
        if (True or isinstance(whereclause,basestring)):
            return sqlalchemy.text(whereclause)
        # it's good already
        return whereclause










    def makedbtables_all(self):
        """
        Ask sqlalchemy to build the actual tables for the models that have been created so-far.
        NOTE: we may call this more than once; once initially for some early models we need, and then later after startup completes.
        """
        for key,val in self.alchemyhelpers.iteritems():
            val.sqlahelper_makedbtables_all()


    def makedbtable_one(self, tablename):
        # create one table if it doesn't exist
        for key,val in self.alchemyhelpers.iteritems():
            val.sqlahelper_makedbtable_one(tablename)







