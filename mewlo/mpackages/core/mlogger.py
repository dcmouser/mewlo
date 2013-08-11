"""
mlogger,py
This module defines subclassed logger classes specialized for Mewlo.

"""

# helper imports
from helpers.logger.logger import LogMessage





class MewloLogMessage(LogMessage):
    """
    MewloLogMessage- a single loggable event/message, derived from the LogMessage class.
    It differs by recording the REQUEST that the log message is related to, and by overriding some display info.
    """

    def __init__(self, msg, request, mtype, level, id, extras):
        # call parent constructor
        super(MewloLogMessage,self).__init__(msg, type, level, id, extras)
        # add mewlo properties to it (request)
        self.request = request



    def as_logline(self):
        """Get the LogMessage as a string suitable for writing to a log file."""
        retstr = str(self.msg)
        if (self.request!=None):
            retstr += " | " + self.request.get_path()
        return retstr



    def debug(self, indentstr=""):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        return indentstr+"MewloLogMessage: "+str(self.msg)

