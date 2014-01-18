"""
logtarget_database.py
LogTarget subclass that writes to database table
"""

# future imports
from __future__ import print_function

# mewlo imports
from .. import mglobals

# helper imports
from mlogger import MewloLogTarget

# python imports
import sys





class MewloLogTarget_Database(MewloLogTarget):
    """LogTarget_File - target that can write log lines to a file."""

    def __init__(self, baseclass, tablename):
        # parent constructor
        super(MewloLogTarget_Database, self).__init__(logformatter=None)
        #
        self.baseclass = baseclass
        self.tablename = tablename
        self.logclass = None
        self.isprocessing = False
        #
        self.dbmanager = None



    def startup(self, mewlosite, eventlist):
        """Startup everything."""
        # create the logging class we will use for this table
        customclassname = self.baseclass.__name__ + '_' + self.tablename
        self.dbmanager = mewlosite.dbmanager
        # NOTE: we call create_derived_dbmodelclass() to dynamically on the fly create a new model class based on an existing one, but with unique table, etc.
        self.logclass = self.dbmanager.create_derived_dbmodelclass(self, self.baseclass, customclassname, self.tablename)
        # now register it
        self.dbmanager.register_modelclass(self, self.logclass)
        # parent
        super(MewloLogTarget_Database,self).startup(mewlosite, eventlist)

    def shutdown(self):
        """Shutdown everything, we are about to exit."""
        super(MewloLogTarget_Database,self).shutdown()


    def readytowrite(self):
        """Before we can save items we need to be started up AND the base class used for logging needs to have been registered."""
        return (self.get_startedup() and self.logclass!=None and self.logclass.get_isreadytodb())


    def process(self, logmessage, flag_isfromqueue):
        """
        Called by logger parent to actually do the work.
        We overide this in our subclass to do actual work.
        """

        # sqlalchemy does NOT like us trying to db log it's own messages while in the middle of debugging
        if ('source' in logmessage.fields):
            if (logmessage.fields['source']=='sqlalchemy'):
                if (not flag_isfromqueue):
                    self.queuelog(logmessage)
                    return False

        # if not flushing but there are waiting, do them first
        if (not flag_isfromqueue and len(self.logqueue)>0):
            self.flushqueue()

        bretv = self.write(logmessage, flag_isfromqueue)
        return bretv




    def write(self, logmessage, flag_isfromqueue):
        """Write out the logmessage to the file."""

        # we must disable sqlalchemy logging while we do this or it will recurse
        self.dbmanager.sqlalchemydebuglevel_temporarydisable()

        # build a modelobj for the log message
        modelobj = self.logclass.new()
        # now write the logmessage fields to it (putting unknown fields in serialized dict)
        modelobj.map_dict_to_properties(logmessage.fields)
        # now save it
        modelobj.save()

        # now we can turn back on sqlalchemy logging
        self.dbmanager.sqlalchemydebuglevel_donetemporarydisable()

        # return True saying it was written
        return True





    def get_nicelabel(self):
        return self.__class__.__name__ + " (Database table '{0}')".format(self.tablename)


