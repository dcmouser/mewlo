"""
misc.py
This module contains misclenaeous helper functions.
"""


# helper imports
from ..eventlog import mevent
from ..eventlog import mexceptionplus

# python imports
import re
import pickle
import time







def get_value_from_dict(thedict, keyname, defaultval=None):
    """Very simple function to get value from dictionary or fall back to default value."""
    if (keyname in thedict):
        return thedict[keyname]
    return defaultval






def readfile_asjson(filepath, nicelabel):
    """
    Read a file and return json dictionary
    :return: EFailure on error
    """

    # python libraries
    import json

    # make sure filename is nonblanck
    if (filepath == ""):
        return None, mevent.EFailure(nicelabel+" has blank info file path")

    # open the file and load into a string
    try:
        # open file for reading, and read it into string
        file = open(filepath, 'r')
    except Exception as exp:
        return None, mevent.EException("Failed to open '{0}' from path '{1}'.".format(nicelabel,filepath), exp=exp, flag_traceback=False )

    # read the file
    try:
        jsonstr = file.read()
    except Exception as exp:
        return None, mevent.EException("Opened but failed to read contents of '{0}' from path '{1}'.".format(nicelabel,filepath), exp=exp, flag_traceback=False )
    finally:
        file.close()

    # parse string as json
    try:
        jsondict = json.loads(jsonstr)
    except Exception as exp:
        return None, mevent.EException("Syntax error parsing json code in '{0}' from file '{1}'.".format(nicelabel,filepath), exp=exp, flag_traceback=True)

    # success
    return jsondict, None








def does_dict_filter_match(object_features, feature_filter):
    """Compare feature_filter against objectfeatures, return True if its a match."""
    # ATTN: we migh want to implement more sophisticated filter "DSL language" in the future
    # walk keys in feature_filter dictionary, and return False if object does not match on any of them
    for keys in feature_filter:
        if (not key in object_features):
            return False
        if ((object_features[key] != feature_filter[key]) and (feature_filter[key] != '*')):
            return False
    # nothing failed, so it's a match!
    return True






def resolve_expand_string(patternstring, replacementdict, depthcount=0):
    """Do recursive replacement in string with patterns."""
    # print "ATTN:DEBUG Asked to exp '"+patternstring+"' with :" + str(replacementdict)

    def resolve_expand_string_replacevar(match):
        """Recursive call to expand contents."""
        if (depthcount>99):
            # bailout of out-of-control recursion
            return retv
        # recursively expand
        try:
            retv = resolve_expand_string(replacementdict[match.group(1)], replacementdict, depthcount+1)
        except Exception as exp:
            mexceptionplus.reraiseplus(exp, "Could not find a key '{0}' in alias replacement dictionary: {1}".format(match.group(1),replacementdict))
        return retv

    regexpat = r'\$\{([a-zA-Z0-9\_\-]+)\}'
    retv = re.sub(regexpat, resolve_expand_string_replacevar, patternstring)
    return retv




def append_text(mainstring, newstring, separator = "; "):
    """Add some text to a string which is accumulating it."""
    if (mainstring==None or mainstring==''):
        return newstring
    return mainstring + separator + newstring





def serialize_for_readability(obj):
    """
    Serialize an object (usually a list or dictionary), and if there are objects we can't serialize, just serialize them as a string.
    That is, we don't mind if objects in the list/dictionary can't be unserialized as objects, we just care about top level separation.
    """
    try:
        # first we try a direct simple pickle
        serializedtext = pickle.dumps(obj)
    except Exception as exp:
        # ok we hit an exception here, so now walk list/dictionary and use strings for objects
        safeobj = serialize_for_readability_makesafe(obj)
        serializedtext = pickle.dumps(safeobj)
    return serializedtext


def serialize_for_readability_makesafe(obj):
    """
    Helper function for serialize_for_readability(obj) that converts items of a list/dictionary into simpler objects
    """
    try:
        if (isinstance(obj, list)):
            # it's a list
            safeobj = []
            for item in obj:
                safeobj.append(serialize_for_readability_makesafe(item))
        elif (isinstance(obj, dict)):
            # it's a dict
            safeobj = {}
            for key,val in obj.iteritems():
                safeobj[key] = serialize_for_readability_makesafe(val)
        elif (isinstance(obj, tuple)):
            # it's a tuple
            safeobj = ()
            for item in obj:
                safeobj += serialize_for_readability_makesafe(item)
        elif (isinstance(obj, (int, str, float, bool))):
            # its primitive type we can use directly
            safeobj = obj
        elif ((hasattr(obj,'logserialize'))):
            # use custom logserialize function
            safeobj = obj.logserialize()
            pass
        elif ((hasattr(obj,'dumps'))):
            # use default dumpes function
            # ATTN: do we really want to do this? It could result is a BIG text blob for some objects..
            safeobj = obj.dumps()
        else:
            # something else
            safeobj = str(obj)
    except Exception as exp:
        # couldnt do anything with it, so return a simple string with it's name
        #safeobj = 'UNKNOWNOBJECT'
        raise
    #
    return safeobj






def compare_versionstrings_isremotenewer(localversion, remoteversion):
    """
    Return true if remote version is newer.
    We expect versions to be of format ##.##.## where ## can be 0 leading or not, and .05 is same a .5, we integerize the #s
    :return: tuple (isremotenewer, failure)
    """
    if (localversion == None):
        localversionparts = []
    else:
        localversionparts = localversion.split('.')
    if (remoteversion == None):
        remoteversionparts = []
    else:
        remoteversionparts = remoteversion.split('.')

    # loop through the parts
    minlen = min(len(localversionparts),len(remoteversionparts))
    for i in range(0,minlen):
        localpartval = int(localversionparts[i])
        remotepartval = int(remoteversionparts[i])
        if (localpartval<remotepartval):
            # remote version is newer!
            return True, None
        elif (localpartval>remotepartval):
            # local version is newer (!)
            return False, mevent.EError("Locally installed version ({0}) is newer than remote version ({1}).".format(localversion,remoteversion))
        # a match for this part of version, keep checking

    # all parts in loop match, so now the only question is if there are more parts not yet parsed in remote
    if (len(localversionparts) < len(remoteversionparts)):
        # remote version is newer becase it has an additional part (i.e 2.0 < 2.0.000001
        return True, None

    # local version is same or newer
    return False, None




def strvalnone(val,noneval='n/a'):
    """Return string cast of a value or a default value if None."""
    if (val == None):
        return noneval
    return str(val)



