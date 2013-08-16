"""
logger_sinkhole.py
This module defines a derived logging class that just swallows messages and does nothing.
"""

# helper imports
from logger import LogTarget





class LogTarget_Sinkhole(LogTarget):
    """Target that hands off log writing duties to standard python logging classes."""


    def __init__(self):
        # parent constructor
        super(LogTarget_Python, self).__init__()



    def process(self, logmessage):
        """
        Called by logger parent to actually do the work.
        We overide this in our subclass to do actual work.
        """
        pass

