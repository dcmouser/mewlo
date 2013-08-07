"""
This module contains functions that can lookup and return a reference to a function in a module, where both are specified by module imports or dotted strings.
"""



# python modules
from types import ModuleType
import sys
import os
import traceback





def find_callable(callableroot, callableobj):
    """
    Given a dotted path, and an optional root package, find the callable.

    This is really the only function in this module that the user should ever have to invoke; the rest of the functions are called by this one.

    For more info on the approach, see http://stackoverflow.com/questions/6643324/how-is-calling-module-and-function-by-string-handled-in-python

    :param callableroot: None | string to prefix to dotted path | imported package(module) to use as root of dotted lookup
    :param callableobj: string representing a dotted path to look up; the last element is treated as function name, and everything before that is treated as module name to lookup

    :return: tuple (funcreferce, errorstr)

    :todo: support python egg format of "package.module:object"
    """

    # if callableobj is not a string, then we are DONE and can either just return it if its callable, or throw an error if its not callable
    if (not isinstance(callableobj, basestring)):
        if (callable(callableobj)):
            return (callableobj, "")
        return (None,"The provided object ("+str(callableobj)+") is not a 'callable'.")

    # ok so we know that callableobj is a string
    callablepath = callableobj

    # split dotted path into modules (might be blank), and last item is a functionname
    modulepath, functionname = split_dottedpath_modulepath_and_funcname(callablepath)

    # now that we have (possibly None) modulepath string, let's find it from root (which might be None or an actual package object)
    (mod, errorstr) = find_module_from_dottedpath(callableroot, modulepath)
    if (mod==None):
        return (None, errorstr)

    # now we have the module OBJECT where the function is located, so we can try to lookup the function from the module
    (func, errorstr) = find_function_from_module_and_dottedpath(mod, functionname)
    if (func==None):
        return (None, "Imported module '"+modulepath+"' but "+errorstr)

    # success
    return (func, "")



def find_callable_throwexception(callableroot, callableobj):
    """
    Just call find_callable but throw an exception if not found; more useful for finding errors quickly
    """

    (callable, errorstr) = find_callable(callableroot, callableobj)
    if (errorstr!=""):
        raise Exception(errorstr)
    return callable




def find_module_from_dottedpath(callableroot, modulepath):
    """
    Internal helper funciton for finding a callable by string or module itself.
    Given a dotted path to a module, look up and return the module.
    """

    # if a root is specified, we use it
    if (callableroot!=None):
        # we have a root
        if (isinstance(callableroot, basestring)):
            # root is a string so just add it to module path and then look for module by string dottedpath
            modulepath = callableroot + "." + modulepath
            (mod,errorstr) = find_module_from_dottedpath_bystring(modulepath)
        elif (isinstance(callableroot, ModuleType)):
            # root is actually a package module, so just find modulepath dottedstring relative to the root package module
            (mod,errorstr) = find_module_from_dottedpath_relativetopackage(callableroot, modulepath)
        else:
            # no idea what callableroot IS
            mod = None
            errorstr = "Unknown callableroot ("+str(callableroot)+") type; not attempting to load modulepath: "+modulepath
    else:
        # no root, so just import the module as a string
        (mod,errorstr) = find_module_from_dottedpath_bystring(modulepath)
    return (mod,errorstr)



def find_module_from_dottedpath_bystring(modulepath):
    """
    Internal helper funciton for finding a callable by string.
    Given a dotted path to a module, look up and return the module.
    """

    # call __import__ to load the module and get a reference to it; the ["dummyval"] arg is needed to trick it to return a module reference
    try:
        mod = __import__(modulepath, globals(), locals(), ["dummyval",], -1)
    except Exception as exp:
        return (None, "Failed to module import '"+modulepath+"': "+str(exp))
    return (mod, "")



def find_module_from_dottedpath_relativetopackage(parentmodule, modulepath):
    """
    Internal helper funciton for finding a callable by string.
    Given a dotted path to a module relative to a parent, look up and return the module.
    """

    # ATTN: i tried lots of approaches to directly ask the parentmodule to import modulepath, but could not get it to work, so i've fallen back on this method; i'm not sure what if any downsides it might have in terms of scope confusion..
    #  it does seem to solve the problem of the getting the parentmodule __name__ to be a dotted path and not just the pure name of the module, which helps it work regardless of where main script is run from
    fullpath = parentmodule.__name__
    if (modulepath != ""):
        fullpath = fullpath + "." + modulepath
    return find_module_from_dottedpath_bystring(fullpath)



def find_function_from_module_and_dottedpath(mod, functionname):
    """
    Internal helper funciton for finding a callable by string.
    Return the callable function attribute in the given module.
    """

    # we have an imported module package, not find the function attribute by name
    try:
        func = getattr(mod, functionname)
    except Exception as exp:
        return (None, "failed to find function '"+functionname+"': "+str(exp))
    #
    return (func, "")



def split_dottedpath_modulepath_and_funcname(dottedname):
    """
    Internal helper funciton for finding a callable by string.
    Split off the token after the last dot and return a tuple of (string-less-the-last-token, last-token)
    """

    from string import join
    #
    modulepath = join(dottedname.split('.')[:-1],'.')
    functionname = dottedname.split('.')[-1]
    #
    return (modulepath, functionname)
















def importmodule_bypath(path):
    """Import a module by path."""
    return do_importmodule_bypath_version1(path)



def do_importmodule_bypath_version1(path):
    """Internal helper function. Load a python module import by explicit path; version1 uses imp.load_source"""
    dynamicmodule = None
    errorstr = ""

    name, ext = os.path.splitext(os.path.basename(path))
    modulename = "DynamicallyLoadedPackage_"+name

    try:
        dynamicmodule = imp.load_source(modulename, path)
    except Exception as exp:
        errorstr = "Failure to load_source module ("+path+"): "+str(exp)+"; STACK TRACEBACK: "+traceback.format_exc()

    return (dynamicmodule, errorstr)


def do_importmodule_bypath_version2(path):
    """Internal helper function.Load a python module import by explicit path; version2 uses find_module and load_module"""
    dynamicmodule = None
    errorstr = ""
    file = None

    # get name+path
    name, ext = os.path.splitext(os.path.basename(path))
    dirpath = os.path.dirname(path)

    # find the module
    try:
        (file, filename, data) = imp.find_module(name, [dirpath])
        if (not file):
            errorstr = "Failure to find module ("+path+")."
    except Exception as exp:
        errorstr = "Failure to find module ("+path+"): "+str(exp)
    # load it after find
    if (file):
        try:
            dynamicmodule = imp.load_module(name, file, filename, data)
        except Exception as exp:
            errorstr = "Failure to load module ("+path+"): "+str(exp)+"; STACK TRACEBACK: "+traceback.format_exc()
        file.close()
    # return it
    return (dynamicmodule, errorstr)


def do_importmodule_bypath_version3(path):
    """Internal helper function.Load a python module import by explicit path; version3 appends to sys path"""
    dynamicmodule = None
    errorstr = ""

    # save previous sys path
    oldpath = sys.path

    #append path of new module to load
    dirpath = os.path.dirname(path)
    name, ext = os.path.splitext(os.path.basename(path))
    sys.path.append(dirpath)

    # do the import
    try:
        dynamicmodule = __import__(name)
    except Exception as exp:
        errorstr = "Failure to import package code module ("+path+"): "+str(exp)+"; STACK TRACEBACK: "+traceback.format_exc()

    # reset sys path
    sys.path = oldpath

    # return it
    return (dynamicmodule, errorstr)
