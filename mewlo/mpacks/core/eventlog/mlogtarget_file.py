"""
logger_filetarget.py
This module defines a derived logging hey class that implements file logging.
"""

# future imports
from __future__ import print_function

# mewlo imports
from mlogger import MewloLogTarget
import mlogformat_pretty
# mewlo imports
from ..constants.mconstants import MewloConstants as mconst

# python imports
import sys





class MewloLogTarget_File(MewloLogTarget):
    """MewloLogTarget_File - target that can write log lines to a file."""





    def __init__(self, filename=None, filemode = mconst.DEF_LOG_TARGET_filemode_default, logformatter=None):
        # default logformatter is pretty
        if (logformatter==None):
            logformatter = mlogformat_pretty.MewloLogFormatter_Pretty()
        # parent constructor
        super(MewloLogTarget_File, self).__init__(logformatter=logformatter)
        # we start out with closed file and will only open on first write
        self.filep = None
        # save the filename and file open mode (could be write or append)
        self.set_fileinfo(filename, filemode)


    def process(self, logmessage, flag_isfromqueue):
        """
        Called by logger parent to actually do the work.
        We overide this in our subclass to do actual work.
        """
        return self.write(logmessage, flag_isfromqueue)




    def set_fileinfo(self, filename, filemode):
        """Set the filename we will open and write to on first write."""
        # Close any exisitng file if its already open.
        self.closefile_ifopen()
        # remember the filename and desired open more
        self.filename = filename
        self.filemode = filemode



    def closefile_ifopen(self):
        """Close the file if it's already open."""
        if (self.filep == None):
            return
        # close file and clear it
        self.filep.close()
        self.filep = None



    def get_openfile(self):
        """
        Open the file if it's not open.
        :return: the file reference so to use.
        """

        # this will throw an exception if file cannot be opened
        if (self.filep == None):
            self.filep = open(self.filename, self.filemode)
        return self.filep



    def write(self, logmessage, flag_isfromqueue):
        """Write out the logmessage to the file."""
        # ensure file is open. this will throw exception if there is an error opening the file, and caller will handle exception by disabling us, etc.
        filep = self.get_openfile()
        # get log line as string
        if (self.logformatter != None):
            outline = self.logformatter.format_logmessage_as_string(logmessage)
        else:
            outline = logmessage.as_string()
        # print it (this could throw an exception if write failes)
        print(outline, file=filep)
        # flush file right away so file is written before closing
        filep.flush()
        # return True saying it was written
        return True



    def shutdown(self):
        """Shutdown everything, we are about to exit."""
        # important that we call super first so it can do a queue flush before we close file
        super(MewloLogTarget_File,self).shutdown()
        self.closefile_ifopen()


    def get_nicelabel(self):
        return self.__class__.__name__ + " ({0})".format(self.filename)


