"""
logger_sinkholetarget.py
This module defines a derived logging class that just swallows messages and does nothing.
We would use this if we wanted to ignore certain log messages and stop them from progressing to other log targets.
"""

# helper imports
from mlogger import MewloLogTarget





class MewloLogTarget_Sinkhole(MewloLogTarget):
    """Target that just absorbs messages and do nothing."""


    def __init__(self):
        # parent constructor
        super(MewloLogTarget_Sinkhole, self).__init__(logformatter=None)



    def process(self, logmessage):
        """
        Called by logger parent to actually do the work.
        """
        # return True to signify that we were successful
        return True

