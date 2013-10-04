"""
logger_sinkholetarget.py
This module defines a derived logging class that just swallows messages and does nothing.
"""

# helper imports
from logger import LogTarget





class LogTarget_Sinkhole(LogTarget):
    """Target that just absorbs messages and do nothing."""


    def __init__(self):
        # parent constructor
        super(LogTarget_Sinkhole, self).__init__()



    def process(self, logmessage):
        """
        Called by logger parent to actually do the work.
        We overide this in our subclass to do actual work.
        """
        return 0

