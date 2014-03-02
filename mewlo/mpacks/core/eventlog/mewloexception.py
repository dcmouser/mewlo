"""
mewloexception.py
This module contains classes and functions for custom exception handling
They are used to help us easily wrap a python exception in our event class system
"""


# helper imports
from ..helpers.debugging import smart_dotted_idpath
import mevent
from ..constants.mconstants import MewloConstants as mconst

# python imports
import sys







class MewloException(Exception):
    """
    Derived exception.
    """

    def __init__(self, source="", code=None, exp=None, obj=None):

        # if they pass a msg that is not a string, convert it to one
        if (isinstance(source, basestring)):
            self.source = source
            msg = source
        else:
            self.source = source
            msg = str(source)

        # http error code
        self.code = code

        # add dotted id path if found
        if (obj != None):
            msg += smart_dotted_idpath(obj)

        # call parent init
        super(MewloException, self).__init__(msg)

        # init
        self.extramsg = None
        self.origexception = exp

        # we use exc_info so we can get traceback info
        if (exp == None):
            self.tracetext = None
        else:
            self.tracetext = mevent.Event.calc_traceback_text()



    def as_mevent(self):
        """Return the exception as an event."""
        if (isinstance(self.source, mevent.Event)):
            # our original source was an Event so just return that
            return self.source
        # build an event for it
        return mevent.Event({'msg':str(self), 'type':mconst.DEF_EVENT_TYPE_exception})



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

        if (self.origexception != None):
            retstr = str(self.origexception)
        else:
            retstr = ''

        # code?
        if (self.code != None):
            retstr += " [errorcode: {0}] ".format(self.code)


        # ATTN 9/23/13 - not sure about this
        retstr += " [{0}]".format(self.get_supers_string_withnewlines())

        # add extr messages
        if (self.extramsg != None):
            retstr += ". "
            for msg in self.extramsg:
                retstr += " {0}.".format(msg)

        return retstr


    def get_supers_string_withnewlines(self):
        # we want the parent exception text, and fixup newlines
        retstr = super(MewloException, self).__str__()
        retstr = retstr.replace('\\n','\n')
        return retstr





def reraiseplus(exp, msg='', obj=None):
    """Create a new exception, wrapping another exception."""

    # ATTN: TODO -- if exp is ALREADY a MewloException, then rather than WRAPPING it recursively, we might just ADD the new message to it.
    # This would make it easier for us to ADD info as we unwind stack, and probably makes more sense than recursively creating an exception TREE as we unwind
    if (isinstance(exp, MewloException)):
        # the exception we are re-raising is ALREADY an MewloException so rather than create a new MewloException and wrap existing one recursively, we will ammend this exp text and re-raise it
        exp.ammend_reraise_message(msg, obj)
        # ok now re-raise it
        raise

    # get the traceback object for the raise statement below
    exc_info = sys.exc_info()
    traceback_object = exc_info[2]

    # raise a wrapped exception, with original info and traceback
    raise MewloException, (msg, exp, obj), traceback_object

































class MewloException_Web(MewloException):
    """Derived Mewlo exception."""
    def __init__(self, source="", code=404, exp=None, obj=None):
        # call parent init
        super(MewloException_Web, self).__init__(source, code, exp, obj)
        self.flag_dorender = True







class MewloException_NoRender(MewloException_Web):
    """Derived Mewlo exception."""
    def __init__(self, source="", code=404, exp=None, obj=None):
        # call parent init
        super(MewloException_NoRender, self).__init__(source, code, exp, obj)
        # set flag saying we already rendered so catcher does not have to
        self.flag_dorender = False





class MewloException_ObjectDoesNotExist(MewloException_Web):
    """Derived Mewlo exception."""
    def __init__(self, source="", code=404, exp=None, obj=None):
        # call parent init
        super(MewloException_ObjectDoesNotExist, self).__init__(source, code, exp, obj)

