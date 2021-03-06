"""
logger_pythontarget.py
This module defines a derived logging class that uses python logger class to do the actual output.
There are two problems with this code as is:
    * first, when writing the log line out, we are only using the level (if found) and the message, and ignoring any other dictionary values passed in.
    * second, the info about the location of the log message which python logging system is capable of capturing, is lost -- as might be expected it always points back to us here.
To fix these we would like to:
    * first, have a way in the LogTarget_Python of configuring how to add log event dictionary items into the log message, or just serialize them onto the end.
    * second, have a way to grab the location fields of the event creation / original log event, and use that.  One downside to this is the potential impact on cpu of this.
For more clues to this see:
    * http://docs.python.org/2/library/logging.html#logrecord-objects
    * http://docs.python.org/2/howto/logging-cookbook.html#context-info
"""

# future imports
from __future__ import print_function

# helper imports
from mlogger import MewloLogTarget

# python imports
import sys
import logging





class MewloLogTarget_Python(MewloLogTarget):
    """Target that hands off log writing duties to standard python logging classes."""


    def __init__(self, pythonlogger):
        # parent constructor
        super(MewloLogTarget_Python, self).__init__(logformatter=None)
        # we start out with closed file and will only open on first write
        self.pythonlogger = pythonlogger



    def process(self, logmessage, flag_isfromqueue):
        """
        Called by logger parent to actually do the work.
        We overide this in our subclass to do actual work.
        """
        return self.write(logmessage, flag_isfromqueue)




    def write(self, logmessage, flag_isfromqueue):
        """
        Write out the logmessage to the python logger.
        ATTN:TODO - instead of str(logmessage) we should strip out the dictionary keys and write them.
        """


        # values from the log event
        level = logmessage.calc_pythonlogginglevel()
        msg = logmessage.getfield('msg', "")
        loc = logmessage.getfield('loc', None)

        if (loc == None):
            # log it using high level logger call
            self.pythonlogger.log(level, msg)
        else:
            # log it using low-level logger call so we can set location info.
            pythonloggername = self.pythonlogger.name
            pathname = loc['filename']
            lineno = loc['lineno']
            args = None
            exc_info = None
            func = loc['function_name']
            # create record
            pythonlogrecord = self.pythonlogger.makeRecord(pythonloggername, level, pathname, lineno, msg, args, exc_info, func)
            # log record
            self.pythonlogger.handle(pythonlogrecord)
        # return True saying it was written
        return True











    @classmethod
    def make_simple_pythonlogger_tofile(cls, pythonloggername, filepath, level=logging.DEBUG):
        """Class method to make a simple test file logger via python logging system."""
        import logging
        pythonlogger = logging.getLogger(pythonloggername)
        hdlr = logging.FileHandler(filepath)
        pythonformatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s [filepath=%(pathname)s] [filename=%(filename)s] [funcname=%(funcName)s] [module=%(module)s] [lineno=%(lineno)d]")
        hdlr.setFormatter(pythonformatter)
        pythonlogger.addHandler(hdlr)
        pythonlogger.setLevel(level)
        return pythonlogger

