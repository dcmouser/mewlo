"""
logger_filetarget.py
This module defines a derived logging hey class that implements file logging

"""


# python modules (for printing to file)
from __future__ import print_function

# Mewlo helpers
from mewlo.mpackages.core.helpers.logger.logger import LogTarget
from mewlo.mpackages.core.helpers.debugging import smart_dotted_idpath
from mewlo.mpackages.core.helpers.debugging import MewloExceptionPlus, raiseammend





class LogTarget_File(LogTarget):
    """
    LogTarget_File - target that can write log lines to a file
    """

    # class constants
    DEF_FILEMODE_default = 'a'



    def __init__(self, filename=None, filemode = DEF_FILEMODE_default):
        # parent init
        super(LogTarget_File, self).__init__()
        # we start out with closed file and will only open on first write
        self.filep = None
        # save the filename and file open mode (could be write or append)
        self.set_fileinfo(filename,filemode)



    def set_fileinfo(self, filename, filemode):
        """Close any exisitng file if its already open."""
        self.closefile_ifopen()
        # remember the filename and desired open more
        self.filename = filename
        self.filemode = filemode



    def closefile_ifopen(self):
        """Close the file if it's already open."""
        if (self.filep==None):
            return
        # close file and clear it
        filep.close()
        self.filep = None



    def get_openfile(self):
        """
        Open the file if it's not open.
        :return: the file reference so to use.
        """

        # this will throw an exception if file cannot be opened
        if (self.filep==None):
            try:
                self.filep = open(self.filename, self.filemode)
            except Exception as exp:
                # call our helper function to raise a modified wrapper exception which can add some text info, to show who owns the object causing the exception
                raiseammend(exp,"Error occurred in LogTarget: ",self)
        return self.filep



    def writeto_file(self, logmessage):
        """Write out the logmessage to the file."""
        # ensure file is open. this will throw exception if there is an error opening the file
        filep = self.get_openfile()
        # get log line as string
        outline = logmessage.as_logline()
        # print it (this could throw an exception if write failes)
        print(outline, file=filep)
        # flush file right away so file is written before closing
        filep.flush()



    def process(self, logmessage):
        """
        Called by logger parent to actually do the work.
        We overide this in our subclass to do actual work.
        """

        self.writeto_file(logmessage)


