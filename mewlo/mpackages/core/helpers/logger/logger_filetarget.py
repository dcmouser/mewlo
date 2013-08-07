"""
This module defines a derived logging hey class that implements file logging

"""

# python modules

# for printing to file
from __future__ import print_function

# Mewlo helpers
from mewlo.mpackages.core.helpers.logger.logger import LogTarget
from mewlo.mpackages.core.helpers.debugging import smart_dotted_idpath



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
        # close any exisitng file if its already open
        self.closefile_ifopen()
        # remember the filename and desired open more
        self.filename = filename
        self.filemode = filemode


    def closefile_ifopen(self):
        # close the file if it's already open
        if (self.filep==None):
            return
        # close file and clear it
        filep.close()
        self.filep = None


    def get_openfile(self):
        # open the file if it's not open; return it
        # this will throw an exception if file cannot be opened
        if (self.filep==None):
            try:
                self.filep = open(self.filename, self.filemode)
            except Exception as exp:
                # just add some extra info to the exception
                if (False):
                    print("ATTN:DEBUG - failed to open file for logging; identification of log target is: " + smart_dotted_idpath(self))
                    raise exp
                raise IOError("Failed to open file '"+self.filename+"' for logging using filemode '"+self.filemode+"'.  Error occurred in LogTarget: " + smart_dotted_idpath(self))
        return self.filep


    def savetofile(self, logmessage):
        # ensure file is open
        # this will throw exception if there is an error opening the file
        filep = self.get_openfile()
        # get log line as string
        outline = logmessage.as_logline()
        # print it (this could throw an exception if write failes)
        print(outline, file=filep)
        # flush file right away so file is written before closing
        filep.flush()






    def process(self, logmessage):
        # called by logger; we overide this in our subclass to do actual work.
        self.savetofile(logmessage)


