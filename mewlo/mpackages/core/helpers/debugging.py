"""
This module contains miscelaneous functions that aid debugging and logging and error reporting.
"""









def smart_dotted_idpath(obj):
    """
    We try to get a nice dotted path for an object, by assuming it has attribute accessor functions of get_parent and get_id
    We walk up parent path (as far as we are able) and return a dotted path string.
    This function depends on the convention of the object methods get_parent and get_id.
    When there is no get_parent we stop traveling up chaing.
    When there is no get_id we simply use class name.
    """

    retstr = ''
    while (True):
        # get the name of this object itself (or fallback to class name), and add it to the dotted string so far
        objidstr = smart_dotted_idpath_getobjidstr(obj)
        if (retstr==''):
            retstr = objidstr
        else:
            retstr = objidstr + "."+ retstr
        # lookup the parent object if it has one
        obj = smart_dotted_idpath_getparentobj(obj)
        if (obj == None):
            # stop when there is no more parent in the chain
            break
    # return the built string
    return retstr



def smart_dotted_idpath_getobjidstr(obj):
    """Interal use function.  Return the nice idstr for the object; fall back on classname if needed."""

    # find the get_id attribute func
    try:
        getidfunc = getattr(obj, "get_id")
        if (getidfunc and callable(getidfunc)):
            # ok we found a get_id function, so invoke it and get id string
            return getidfunc()
    except:
        # nothing to do if not found
        pass
    # fallback on classname/stringification
    return str(obj)


def smart_dotted_idpath_getparentobj(obj):
    """Interal use function.  Return the parent object of this object, IFF we can find a get_parent function to call; otherwise return None"""

    # find the get_parent attribute func
    try:
        getparentfunc = getattr(obj, "get_parent")
        if (getparentfunc and callable(getparentfunc)):
            # ok we found a get_parent function so get the parent object from it
            return getparentfunc()
    except:
        # nothing to do if not found
        pass
    # not found
    return None













def raiseammend(exp, msg, objforpath=None):
    """Add some additional string info to an exception.  Return the exception object for easier processing."""

    # we use exc_info so we can re-raise the new exception with the ORIGINAL traceback caused by the original exception
    import sys
    exc_info = sys.exc_info()
    # add dotted id path if found
    if (objforpath!=None):
        msg += smart_dotted_idpath(objforpath)
    # raise a wrapped exception, with original info and traceback
    raise MewloExceptionPlus, (msg, exc_info[1]), exc_info[2]






class MewloException(Exception):
    """Base class from which we derive our custom exceptiosn."""
    pass



class MewloExceptionPlus(MewloException):
    """
    Derived exception that can hold a custom string AND a reference to an original exception.
    We may later improve this to better wrap the original exception/traceback.
    Note that Python3 has some built-in features for representing chained/wrapped exceptions.
    """

    def __init__(self, msg, exp):
        # call parent init
        super(MewloExceptionPlus,self).__init__(msg)
        # record original exception
        self.origexception = exp

    def __str__(self):
        # display our custom message created during construction, AND the error for the original exception
        return str(self.origexception) + " ["+super(MewloExceptionPlus,self).__str__()+"]"

