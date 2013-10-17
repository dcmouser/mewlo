"""
exceptionplus.py
This module contains classes and functions for custom exception handling
"""


# helper imports
from ..helpers.debugging import smart_dotted_idpath
from event import Event

# python imports
import sys







class ExceptionPlus(Exception):
    """
    Derived exception that can hold a custom string AND a reference to an original exception.
    We may later improve this to better wrap the original exception/traceback.
    Note that Python3 has some built-in features for representing chained/wrapped exceptions.
    """

    def __init__(self, msg="", exp=None, obj=None):

        # if they pass a msg that is not a string, convert it to one
        if (not isinstance(msg, basestring)):
            msg = str(msg)

        # add dotted id path if found
        if (obj != None):
            msg += smart_dotted_idpath(obj)

        # call parent init
        super(ExceptionPlus, self).__init__(msg)

        # init
        self.extramsg = None
        self.origexception = exp

        # we use exc_info so we can get traceback info
        if (exp == None):
            self.tracetext = None
        else:
            self.tracetext = Event.calc_traceback_text()







    def ammend_reraise_message(self, msg, obj):
        """Add some additional info to our message."""
        # add dotted id path if found
        if (obj != None):
            msg += smart_dotted_idpath(obj)
        # append message
        if (self.extramsg == None):
            self.extramsg = [msg]
        else:
            self.extramsg.append(msg)



    def __str__(self):
        # display our custom message created during construction, AND the error for the original exception
        retstr = str(self.origexception)

        # ATTN 9/23/13 - not sure about this
        retstr += " [" + self.get_supers_string_withnewlines() + "]"

        # add extr messages
        if (self.extramsg != None):
            retstr += ". "
            for msg in self.extramsg:
                retstr += " " + msg + "."
        return retstr


    def get_supers_string_withnewlines(self):
        # we want the parent exception text, and fixup newlines
        retstr = super(ExceptionPlus, self).__str__()
        retstr = retstr.replace('\\n','\n')
        return retstr





def reraiseplus(exp, msg='', obj=None):
    """Create a new exception, wrapping another exception."""

    # ATTN: TODO -- if exp is ALREADY a ExceptionPlus, then rather than WRAPPING it recursively, we might just ADD the new message to it.
    # This would make it easier for us to ADD info as we unwind stack, and probably makes more sense than recursively creating an exception TREE as we unwind
    if (isinstance(exp, ExceptionPlus)):
        # the exception we are re-raising is ALREADY an ExceptionPlus so rather than create a new MewloException and wrap existing one recursively, we will ammend this exp text and re-raise it
        exp.ammend_reraise_message(msg, obj)
        # ok now re-raise it
        raise

    # get the traceback object for the raise statement below
    exc_info = sys.exc_info()
    traceback_object = exc_info[2]

    # raise a wrapped exception, with original info and traceback
    raise ExceptionPlus, (msg, exp, obj), traceback_object


