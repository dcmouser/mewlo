# callables.py
"""Support functions to help find dynamic callables"""

# python modules
from types import ModuleType



def findcallable(callableroot, callablestring, flag_throwexception=True):
    # find a callable, class static function
    if (isinstance(callablestring, basestring)):
        (callable, errorstr) = find_callable_from_dottedpath(callableroot, callablestring)
    else:
        callable = callablestring
        errorstr = ""
    #
    if (callable == None):
       errorstr = "failed to find dynamic callable '"+callablestring+"'; "+errorstr+"."
    #
    if (flag_throwexception):
        if (errorstr!=""):
            raise Exception(errorstr)
        return callable
    #
    return (callable, errorstr)



def find_callable_from_dottedpath(callableroot, callablepath):
    # given a dotted path, find the callable
    # see http://stackoverflow.com/questions/6643324/how-is-calling-module-and-function-by-string-handled-in-python
    # return tuple (funcreferce, errorstr)

    if (isinstance(callableroot, basestring) and callableroot!=""):
        callablepath = callableroot + "." + callablepath
        callableroot = None

    # get splitted name
    modulepath, functionname = callablepath_dotsplit(callablepath)

    # get module
    (mod, errorstr) = find_callable_from_dottedpath_module(callableroot, modulepath)
    if (mod==None):
        return (None, errorstr)

    # get function
    (func, errorstr) = find_callable_from_dottedpath_function(mod, functionname)
    if (func==None):
        return (None, "Imported module '"+modulepath+"' but "+errorstr)

    # success
    return (func, "")


def find_callable_from_dottedpath_module(callableroot, modulepath):
    if (callableroot!=None):
        # we have a root
        if (isinstance(callableroot, basestring)):
            modulepath = callableroot + "." + modulepath
            (mod,errorstr) = find_callable_from_dottedpath_module_bystring(modulepath)
        elif (isinstance(callableroot, ModuleType)):
            (mod,errorstr) = find_callable_from_dottedpath_module_relativetopackage(callableroot, modulepath)
        else:
            mod = None
            errorstr = "Unknown callableroot ("+str(callableroot)+") type; not attempting to load modulepath: "+modulepath
    else:
        (mod,errorstr) = find_callable_from_dottedpath_module_bystring(modulepath)
    return (mod,errorstr)



def find_callable_from_dottedpath_module_bystring(modulepath):
    try:
        mod = __import__(modulepath, globals(), locals(), ["dummyval",], -1)
    except Exception as exp:
        return (None, "Failed to module import '"+modulepath+"': "+str(exp))
    return (mod, "")


def find_callable_from_dottedpath_module_relativetopackage(parentmodule, modulepath):
    # ATTN: i tried lots of approaches to directly ask the parentmodule to import modulepath, but could not get it to work, so i've fallen back on this method; i'm not sure what downsides it might have in terms of scope confusion..
    fullpath = parentmodule.__name__ + "." + modulepath
    return find_callable_from_dottedpath_module_bystring(fullpath)


def find_callable_from_dottedpath_function(mod, functionname):
    try:
        func = getattr(mod, functionname)
    except Exception as exp:
        return (None, "failed to find function '"+functionname+"': "+str(exp))
    #
    return (func, "")


def callablepath_dotsplit(dottedname):
    from string import join
    #
    modulepath = join(dottedname.split('.')[:-1],'.')
    functionname = dottedname.split('.')[-1]
    #
    return (modulepath, functionname)




