"""
callables.py
This module contains functions that can lookup and return a reference to a function in a module, where both are specified by module imports or dotted strings.
These functions are used, for example, in mcontroller.py where a site specifies the controller function associated with a route.
"""


# helper imports
from ..eventlog.mevent import EFailure, EException

# python imports
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

    :return: funcreference

    :todo: support python egg format of "package.module:object"

    ATTN: we currently use an exception here because we treat this like a fatal error.
    If instead we wanted callers to be able to resume fromt his, we might return EFailures instead
    """

    # Note that many of the function calls below can throw exceptions

    # if callableobj is not a string, then we are DONE and can either just return it if its callable, or throw an error if its not callable
    if (not isinstance(callableobj, basestring)):
        if (callable(callableobj)):
            return callableobj
        raise TypeError("The provided object '{0}' is not a 'callable'.".format(str(callableobj)))

    # ok so we know that callableobj is a string
    callablepath = callableobj

    # split dotted path into modules (might be blank), and last item is a functionname
    modulepath, functionname = split_dottedpath_modulepath_and_funcname(callablepath)

    # now that we have (possibly None) modulepath string, let's find it from root (which might be None or an actual package)
    mod = find_module_from_dottedpath(callableroot, modulepath)

    # now we have the module OBJECT where the function is located, so we can try to lookup the function from the module
    func = find_function_from_module_and_dottedpath(mod, functionname)

    # success
    return func









def importmodule_bypath(path):
    """Import a python module by file path."""
    # we had several versions of the do_import function, hence the simple redirection call here
    return do_importmodule_bypath(path)
































# ---------------------------------------------------------------------------
# Private functions
# ---------------------------------------------------------------------------



def find_module_from_dottedpath(callableroot, modulepath):
    """
    Internal helper funciton for finding a callable by string or module itself.
    Given a dotted path to a module, look up and return the module.
    """

    # if a root is specified, we use it
    if (callableroot != None):
        # we have a root
        if (isinstance(callableroot, basestring)):
            # root is a string so just add it to module path and then look for module by string dottedpath
            modulepath = callableroot + '.' + modulepath
            mod = find_module_from_dottedpath_bystring(modulepath)
        elif (isinstance(callableroot, ModuleType)):
            # root is actually a package module, so just find modulepath dottedstring relative to the root package module
            mod = find_module_from_dottedpath_relativetopackage(callableroot, modulepath)
        else:
            # no idea what callableroot IS
            raise LookupError("Unknown callableroot '{0}' type; not attempting to load modulepath: '{1}'".format(str(callableroot),modulepath))
    else:
        # no root, so just import the module as a string
        mod = find_module_from_dottedpath_bystring(modulepath)
    return mod



def find_module_from_dottedpath_bystring(modulepath):
    """
    Internal helper funciton for finding a callable by string.
    Given a dotted path to a module, look up and return the module.
    """

    # call __import__ to load the module and get a reference to it; the ["dummyval"] arg is needed to trick it to return a module reference
    mod = __import__(modulepath, globals(), locals(), ["dummyval",], -1)
    return mod



def find_module_from_dottedpath_relativetopackage(parentmodule, modulepath):
    """
    Internal helper funciton for finding a callable by string.
    Given a dotted path to a module relative to a parent, look up and return the module.
    """

    # ATTN: i tried lots of approaches to directly ask the parentmodule to import modulepath, but could not get it to work, so i've fallen back on this method; i'm not sure what if any downsides it might have in terms of scope confusion..
    #  it does seem to solve the problem of the getting the parentmodule __name__ to be a dotted path and not just the pure name of the module, which helps it work regardless of where main script is run from
    fullpath = parentmodule.__name__
    if (modulepath != ''):
        fullpath = fullpath + '.' + modulepath
    return find_module_from_dottedpath_bystring(fullpath)



def find_function_from_module_and_dottedpath(mod, functionname):
    """
    Internal helper funciton for finding a callable by string.
    Return the callable function attribute in the given module.
    """

    # we have an imported module package, not find the function attribute by name
    func = getattr(mod, functionname)
    return func



def split_dottedpath_modulepath_and_funcname(dottedname):
    """
    Internal helper funciton for finding a callable by string.
    Split off the token after the last dot and return a tuple of (string-less-the-last-token, last-token)
    """

    from string import join
    #
    modulepath = join(dottedname.split('.')[:-1], '.')
    functionname = dottedname.split('.')[-1]
    #
    return (modulepath, functionname)





























def do_importmodule_bypath(filepath, flag_tryinitfiletoo=True):
    """
    Internal helper function. Load a python module import by explicit path.
    """

    # init
    dynamicmodule = None
    failure = None

    # extract name, which is the filename with no directory and no extension
    name, ext = os.path.splitext(os.path.basename(filepath))
    # get just the path to the directory containing the file
    dirpath = os.path.dirname(filepath)


    #print "IN do_importmodule_bypath with name = {0} and dirpath = {1}.".format(name,dirpath)


    # Now this is the critical part that saves us from python double import and allow relative importing from this dynamic module, without needing to adjust the system path.
    # Essentially, the code you will find for importing a python file by absolute filename path (as you might do in plugin loading), works to load the module,
    #  but creates it in a kind of alternate univers where it doesnt know where it is w.r.t. relative importing; so that an attempt to do a relative import from this dynamically loaded module will fail with "module not found"
    # This is quite ridiculous, but not nearly as bad as what happens when you try to work around this.
    # The best way I initially found to solve this was to temporarily change the system path to include the dynamically loading module (and then we can even change it back afterwards).
    # This works great because the module is found and can even be loaded with a simple import statment after you include its path on the python path, and then relative imports work.
    # When you do this -- and you will find code on the internet which suggests it as a good solution, everything seems to work great.
    # However, there is a terribly awful, pernicious, f*cked up thing that python does behind the scenes..
    # What happens is that this newly dynamically loaded module lives in an even worse alternate reality than the one we described above.
    # In this case, it will be able to find relative imports -- but it will not realize that they are the same modules that have already been imported.
    # It will then re-import and created shadow versions of already loaded modules, wiping out class and global variables in the process.
    # It is beyond evil and pretty outrageous.  You can find some discussion here:
    # http://stackoverflow.com/questions/4798589/what-could-cause-a-python-module-to-be-imported-twice
    # http://python-notes.boredomandlaziness.org/en/latest/python_concepts/import_traps.html (The double import trap)
    # So, what's the solution?
    # The solution is to do a rather annoying bit of fix up before calling imp.load_module, in order to ensure
    # that the internal module dotted name given to the imported module is expressed relatively to something on the existing python path, if possible
    # This is not trivial to do.

    # The normal suggested dumb way to specify the first parameter to imp.load_module -- this will work but kill relative importing
    #imploadname = name

    # So instead, we need to figure out a dotted name for the module, relative to *something* on the current python path.
    # and if we cannot find this module relative to the python path, we need to ADD it's directory to the python path
    (imploadname, flag_didaddtopath) = guess_module_importname_or_adjust_pythonpath(dirpath, name)
    # test
    #imploadname = 'mewlo.mpacks.core.core_mpack'


    # debug display
    #print "ATTN:DEBUG - in import_module_bypath with filepath = '{0}' and name = '{1}' and dirpath = '{2}' and using imploadname = '{3}'.".format(filepath, name, dirpath, imploadname)

    # does it already exist?
    if (imploadname != '' and imploadname in sys.modules):
        #print "****** ATTN: MODULE {0} ALREADY LOADED NOT RELOADING! ******".format(imploadname)
        return sys.modules[imploadname], None


    # ok this is a strange python thing.
    # It does not seem to like if we directly import a module that is discoverable via dotted path,
    #  and then try to perform absolute imports in it;  it gives a warning like "Warning: Parent module 'whatever' not ofound while handling absolute import"
    #  so to work around that error, we try importing the parent directory itself whenever we are contemplating importing a file by path
    if (flag_tryinitfiletoo and not flag_didaddtopath):
        #print "TRYING INI PARENT FOLDER PACKAGE RECURSIVE.."
        # ATTN: by passing True as second parameter, we are performing this recursively up the tree; i *think* this is what we want.
        do_importmodule_bypath(dirpath, True)


    # ok let's try the import
    try:
        # find the module
        import imp
        (file, filename, data) = imp.find_module(name, [dirpath])
        #
        #print "+++++++ DYNAMICALLY IMPORTING MODULE '{0}' from '{1}'.".format(imploadname,filename)
        dynamicmodule = imp.load_module(imploadname, file, filename, data)
    except Exception as exp:
        failure = EException("failed to import module by path ("+filepath+")", exp=exp)

    # return it
    return dynamicmodule, failure




def guess_module_importname_or_adjust_pythonpath(dirpath, name):
    """Generate the dotted name to pass to imp.load_module() or modify python path if needed.  See the function do_importmodule_bypath() for a long discussion.
    :return: (imploadname, flag_did_addtopythonpath)
    """

    # convert dirpath to canonical format
    dirpath_canonical = dirpath

    # reset for search
    bestprefix = ''
    bestpath = None
    bestlen = 0
    import sys

    # ok now we are going to walk the loaded modules, looking for ones named __init__.py[c] that are prefixes of our directory
    # that is, we are looking for modules that are really aliases of package directorys, which we can use as our prefix for referring to THIS module
    if (True):
        import re
        regex_initpackagepattern = '__init__\\.py[c]?$'
        regex_initpackagepattern_compiled = re.compile(regex_initpackagepattern)
        modulekeys = sys.modules.keys()
        for key in modulekeys:
            mod = sys.modules[key]
            try:
                if (mod != None):
                    modfile = mod.__file__
                    if (regex_initpackagepattern_compiled.search(modfile)):
                        # it's a package directory module - is it a prefix of our directory?
                        searchpath_canonical = os.path.dirname(modfile)
                        if (dirpath_canonical.startswith(searchpath_canonical)):
                            # yes, it's a prefix of our directory -- is it best so far?
                            thispathlen = len(searchpath_canonical)
                            if (thispathlen>bestlen):
                                # best find so far
                                bestpath = searchpath_canonical
                                bestlen = thispathlen
                                bestprefix = key
                        pass
            except AttributeError:
                pass


    # alternatively, we could look for a prefix anywhere on the system path; this should work too, as an alternate or on top of the first
    # find longest prefix on system system path; but i think it may never be the case that this works where previous fails, so maybe no poing in doing it
    if (bestpath == None):
        for searchpath in sys.path:
            searchpath_canonical = searchpath
            #print "---- CHECKING SYS PATH: '{0}'.".format(searchpath_canonical)
            if (dirpath_canonical.startswith(searchpath_canonical)):
                # found a place that dirpath is relative too -- is it a deeper subdirectory than we have found so far?
                thispathlen = len(searchpath_canonical)
                if (thispathlen>bestlen):
                    # best find so far
                    #print "******************************** BEST SO FAR MATCH: '{0}' **************************".format(searchpath_canonical)
                    bestpath = searchpath_canonical
                    bestlen = thispathlen
                    bestprefix = ''



    # ok did we find a good path to be relative to?
    if (bestpath != None):
        # yes, so lets compute the dotted path for our module relative to this python path item
        # ATTN: there is one small possible cause for failure here -- we are not checking for a valid __init__.py in each subdirectory of the relative path
        #  from our found prefix package to this module.
        #
        #print "Found best system path start for '{0}' to be '{1}' with keyprefix '{2}'.".format(dirpath_canonical, bestpath, bestprefix)
        dirstartpos = bestlen
        # now we want to remove the leading dot that should be found (as long as we haven't matched completely and that python path entries dont end with a directory separator)
        if (dirstartpos < len(dirpath_canonical)):
            if (dirpath_canonical[dirstartpos]=='/' or dirpath_canonical[dirstartpos]=='\\'):
                dirstartpos += 1
        # remove the matching prefix part (which could give us empty string)
        pathsuffix = dirpath_canonical[dirstartpos:]
        # and now change any directory separators to dots
        pathsuffixdotted = pathsuffix
        pathsuffixdotted = pathsuffix.replace('/','.')
        pathsuffixdotted = pathsuffix.replace('\\','.')
        # if pathsuffix is NOT empty, it means we are asking python to walk into a directory starting at some other parent package directory
        # this will FAIL if there is no __init__.py[c] file in the path, so we need to check for that; if not found, then we need to instead add path to sys path and return
        if (pathsuffixdotted != ''):
            # check for __init__
            if (not is_module_directory_importreachable(bestpath, pathsuffixdotted)):
                # since we are not on python path, we won't get the evil shadowed double paths when we add to the python path
                #print "Since requested subdirectory was not walkable (has no __init__ file), instead of trying relative import, we need to append path '{0}' to sys,path".format(dirpath)
                sys.path.append(dirpath)
                # and now we can use just the pure module name, no need for dotted prefix
                return (name, True)
        # ok we are safe, so lets find out how to reference us

        # ok now if there is a pathsuffix, we use it to form full dotted name to use as import
        if (len(pathsuffixdotted)>0):
            imploadname = pathsuffixdotted + '.'+ name
        else:
            # we are already on path, just return name -- no need to do anything else
            imploadname = name
        # now add prefix we found earlier, to good path to use
        if (bestprefix != ''):
            imploadname = bestprefix + '.' + imploadname
        # note that our calculated imploadname may already be loaded (!) the caller must check for this
    else:
        # since we are not on python path, we won't get the evil shadowed double paths when we add to the python path
        sys.path.append(dirpath)
        # and now we can use just the pure module name, no need for dotted prefix
        return (name, True)

    return (imploadname, False)



def is_module_directory_importreachable(startpath, subdirdottedpath):
    # we want to guess it we can import from this directory
    #print "ASKED TO SEE IF WE COULD IMPORT WALK FROM '{0}' to '{1}'.".format(startpath,subdirdottedpath)
    subdirs = subdirdottedpath.split('.')
    checkpath = startpath
    for subdir in subdirs:
        checkpath += '/' + subdir
        if (not does_directory_contain_initpackagefile(checkpath)):
            # fail
            return False

    # all good
    return True


def does_directory_contain_initpackagefile(path):
    import os.path
    if (not os.path.exists(path+'/__init__.py') and not os.path.exists(path+'/__init__.pyc')):
        return False
    return True
