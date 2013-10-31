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



    def startup(self):
        """Startup everything."""
        # create the logging class we will use for this table
        customclassname = self.baseclass.__name__ + '_' + self.tablename
        dbmanager = mglobals.db()
        self.logclass = dbmanager.create_derived_dbmodelclass(self, self.baseclass, customclassname, self.tablename)
        # now register it
        dbmanager.register_modelclass(self, self.logclass)
        #print ("SELFLOGCLASS = "+str(self.logclass.__name__)+" baseclass = "+self.baseclass.__name__)
        # parent
        super(MewloLogTarget_Database,self).startup()

    def shutdown(self):
        """Shutdown everything, we are about to exit."""
        super(MewloLogTarget_Database,self).shutdown()



    def process(self, logmessage, flag_isfromqueue):
        """
        Called by logger parent to actually do the work.
        We overide this in our subclass to do actual work.
        """
        if (not self.get_startedup()):
            # we aren't ready to start logging yet
            if (not flag_isfromqueue):
                self.queuelog(logmessage)
            return 0

        # sqlalchemy does NOT like us trying to db log it's own messages while in the middle of debugging
        if ('source' in logmessage.fields):
            if (logmessage.fields['source']=='sqlalchemy'):
                if (not flag_isfromqueue):
                    self.queuelog(logmessage)
                    return 0

        # if not flushing but there are waiting, do them first
        if (not flag_isfromqueue and len(self.logqueue)>0):
            self.flushqueue()

        retv = self.write(logmessage, flag_isfromqueue)
        return retv




    def write(self, logmessage, flag_isfromqueue):
        """Write out the logmessage to the file."""

        # we must disable sqlalchemy logging while we do this or it will recurse
        mglobals.db().sqlalchemydebuglevel_temporarydisable()

        #print ("ATTN:DEBUG - Logging message: "+str(logmessage))

        # build a modelobj for the log message
        modelobj = self.logclass.new()
        #print("ATTN: DEBUG created modelobj: "+str(modelobj))
        # now write the logmessage fields to it
        modelobj.map_dict_to_properties(logmessage.fields)
        # now save it
        modelobj.save()

        # now we can turn back on sqlalchemy logging
        mglobals.db().sqlalchemydebuglevel_donetemporarydisable()

        # return 1 saying it was written
        return 1





    def get_nicelabel(self):
        return self.__class__.__name__ + " (Database table '{0}')".format(self.tablename)


