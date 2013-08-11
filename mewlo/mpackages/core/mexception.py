"""
mexception.py
This module contains classes and functions for custom exception handling
"""


# helpers
from helpers.debugging import smart_dotted_idpath

# python modules
import sys
import traceback








class MewloError(object):
    """Base class for mewlo-specific error class."""
    pass









def mreraise(exp, msg='', obj=None, site=None, request=None, flag_iscasual=False):
    """Create a mewlo exception, wrapping another exception."""

    # ATTN: TODO -- if exp is ALREADY a MewloExceptionPlus, then rather than WRAPPING it recursively, we might just ADD the new message to it.
    # This would make it easier for us to ADD info as we unwind stack, and probably makes more sense than recursively creating an exception TREE as we unwind
    if (isinstance(exp,MewloExceptionPlus)):
        # the exception we are re-raising is ALREADY a MewloExceptionPlus so rather than create a new MewloException and wrap existing one recursively, we will ammend this exp text and re-raise it
        exp.ammend_reraise_message(msg, obj, site, flag_iscasual)
        # ok now re-raise it
        raise

    # add dotted id path if found
    if (obj!=None):
        msg += smart_dotted_idpath(obj)
    # site info
    if (site==None and obj!=None):
        site=lookup_site_fromobject(obj)

    # we use exc_info so we can re-raise the new exception with the ORIGINAL traceback caused by the original exception
    exc_info = sys.exc_info()
    orig_exception = exc_info[1]
    traceback_object = exc_info[2]

    # add long traceback text
    flag_fulltrace = True
    tracetext = compute_traceback_astext(traceback_object, flag_fulltrace)
    # raise a wrapped exception, with original info and traceback
    raise  MewloExceptionPlus, (msg, site, request, orig_exception, flag_iscasual, tracetext), traceback_object





class MewloException(Exception):
    """Base class from which we derive our custom exceptiosn."""
    pass



class MewloExceptionPlus(MewloException):
    """
    Derived exception that can hold a custom string AND a reference to an original exception.
    We may later improve this to better wrap the original exception/traceback.
    Note that Python3 has some built-in features for representing chained/wrapped exceptions.
    """

    def __init__(self, msg, site, request, exp, flag_iscasual, tracetext):
        # call parent init
        super(MewloExceptionPlus,self).__init__(msg)
        # record info
        self.site = site
        self.request = request
        self.origexception = exp
        self.tracetext = tracetext
        self.extramsg = None
        self.flag_iscasual = flag_iscasual



    def iscasual(self):
        return self.flag_iscasual


    def log_exception(self):
        """Try to log the exception."""
        if (self.site!=None):
            # exception message
            msg = str(self)
            # add traceback text?
            if (self.tracetext != None and self.tracetext!=''):
                msg += " | "+self.tracetext
            # now log it
            self.site.logerror(msg, self.request)



    def ammend_reraise_message(self, msg, obj, site, flag_iscasual):
        """Add some additional info to our message."""
        # add dotted id path if found
        if (obj!=None):
            msg += smart_dotted_idpath(obj)
        # site info
        if (self.site==None and site==None and obj!=None):
            self.site=lookup_site_fromobject(obj)
        # append message
        if (self.extramsg==None):
            self.extramsg = [msg]
        else:
            self.extramsg.append(msg)
        # is casual?
        self.flag_iscasual = flag_iscasual



    def __str__(self):
        # display our custom message created during construction, AND the error for the original exception
        retstr = str(self.origexception)
        retstr += " ["+super(MewloExceptionPlus, self).__str__()+"]"
        # add extr messages
        if (self.extramsg!=None):
            retstr += ". "
            for msg in self.extramsg:
                retstr += " ["+msg+"]."
        if (self.flag_iscasual):
            retstr += " {CASUAL}"
        return retstr















def lookup_site_fromobject(obj):
    """Use getattr to find site up a chain of parents, if possible."""
    if (obj==None):
        return None
    if (hasattr(obj, "get_site")):
        return obj.get_site()
    return None



def compute_traceback_astext(traceback_object, flag_fulltrace):
    """Convert traceback object to nice text.  See http://effbot.org/librarybook/traceback.htm."""
    if (flag_fulltrace):
        tblist = traceback.extract_stack() + traceback.extract_tb(traceback_object)
    else:
        tblist = traceback.extract_stack() + traceback.extract_tb(traceback_object)
    #
    return compute_traceback_astext_fromlist(tblist)



def compute_traceback_astext_fromlist(tblist):
    """Internal helper funciton.  Convert traceback extract list into string."""
    retstr = ''
    #for file, lineno, function, text in traceback.extract_tb(traceback_object):
    for file, lineno, function, text in tblist:
        if (retstr!=''):
            retstr += "; "
        retstr += file +" line #"+str(lineno)+" in "+function+": "+text
    return retstr










def exceptioniscasual(exp):
    """
    Return true if an exception has been explicitly marked as 'casual' -- meaning that it was somewhat expected and program does not need to fatal exit.
    This is a non-object function so that we can call on standard exceptions (in which case the return value is False).
    This function is used in cases where we want to consume an 'expected' exception and continue operations (for example if we want to simply disabled plugins that error).
    It's important that we have this kind of iscasual flag so that we let serious programmatic exceptions (like syntax errors) propagate all the way up the call stack.
    """

    if (isinstance(exp,MewloExceptionPlus)):
        return exp.iscasual()
    return False