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
    #
    while (True):
        objidstr = smart_dotted_idpath_getobjidstr(obj)
        if (retstr==''):
            retstr = objidstr
        else:
            retstr = objidstr + "."+ retstr
        obj = smart_dotted_idpath_getparentobj(obj)
        if (obj == None):
            break
    #
    return retstr




def smart_dotted_idpath_getobjidstr(obj):
    """Return the nice idstr for the object; fall back on classname if needed."""
    # find the get_id attribute func
    try:
        getidfunc = getattr(obj, "get_id")
        if (getidfunc and callable(getidfunc)):
            return getidfunc()
    except:
        pass
    # fallback on classname/stringification
    return str(obj)



def smart_dotted_idpath_getparentobj(obj):
    """."""
    # find the get_parent attribute func
    try:
        getparentfunc = getattr(obj, "get_parent")
        if (getparentfunc and callable(getparentfunc)):
            return getparentfunc()
    except:
        pass
    # not found
    return None
