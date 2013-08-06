"""
This module defines classes and functions that implement file logging

"""


# python modules
from __future__ import print_function



class LogTarget_File(object):
    """
    LogTarget_File - target that can write log lines to a file
    """

    def __init__(self, filename=None, filemode = 'w'):
        # parent init
        super(LogTarget_File, self).__init__()
        self.filep = None
        #
        self.set_fileinfo(filename,filemode)

    def set_fileinfo(self, filename, filemode):
        self.closefile_ifopen()
        self.filename = filename
        self.filemode = filemode


    def closefile_ifopen(self):
        if (self.filep==None):
            return
        # close file and clear it
        filep.close()
        self.filep = None

    def get_openfile(self):
        if (self.filep==None):
            self.filep = open(self.filename, self.filemode)
        return self.filep


    def savetofile(self, logmessage):
        # ensure file is open
        filep = self.get_openfile()
        if (filep==None):
            # ATTN:TODO throw exception
            return False
        # get log line as string
        outline = logmessage.as_logline()
        # print it
        print(outline, file=filep)
        # flush file?
        filep.flush()






    def run(self, logmessage):
        self.savetofile(logmessage)
        pass


