"""
This module defines subclassed logger classes.

"""

from helpers.logger.logger import LogMessage


class MewloLogMessage(LogMessage):
    """
    MewloLogMessage- a single loggable event/message
    """

    def __init__(self, msg, request, mtype, level, id, extras):
        # call parent constructor
        super(MewloLogMessage,self).__init__(msg, type, level, id, extras)
        # add mewlo properties to it
        self.request = request

    def as_logline(self):
        return str(self.msg) + " | " + self.request.get_path()



    def debug(self, indentstr=""):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        return indentstr+"MewloLogMessage: "+str(self.msg)



