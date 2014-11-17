"""
misc.py
This module contains misclenaeous helper functions.
"""




# python imports
import os
import re
import pickle
import time
import hashlib, uuid



# constant
DEF_mnamespace_separator = '::'
DEF_mnamespace_separator_forpath = '_'




def calc_modulefiledirpath(file_define, subpath = None):
    """Called like calc_modulefiledir(__file__) to return directory path to current module."""
    path = os.path.dirname(os.path.realpath(file_define))
    if (subpath):
        path += '/' + subpath
    return path




def get_value_from_dict(thedict, keyname, defaultval=None):
    """Very simple function to get value from dictionary or fall back to default value."""
    if (keyname in thedict):
        return thedict[keyname]
    return defaultval









def inherited_mnamespace(mnamespace_parent, mnamespace_child):
    """
    Combine parent and child mnamespace strings.
    This function is called on rare occasions where we are traversing a hierarchy of structures (see build_structure function in mroute.py), and we want a namespace from a parent to be inherited by a child,
    BUT want to deal with a case where the child might have an explicit namespace provided (and not parent).
    So, the basic logic here is, if the child namespace is specified, use that; if not, use the parent namespace (blank or not).
    NOTE: As described above, if both are specified we should use child, however we might log a message warning that it's possibly an issue.
    """
    if (mnamespace_parent and mnamespace_child):
        # issue a warning? and drop down
        pass
    if (mnamespace_child):
        return mnamespace_child
    # return parent namespace (which might be empty)
    return mnamespace_parent



def mnamespacedid(mnamespace, childid):
    """Combine parent and child mnamespace strings."""
    if (not childid):
        childid = 'ANONYMOUS'
    # ATTN: TODO -- might we check if childid already has a namespace, and skip adding it if so?
    if (True and childid.find(DEF_mnamespace_separator)!=-1):
        return childid
    if (mnamespace):
        return mnamespace + DEF_mnamespace_separator + childid
    # NOTE: IMPORTANT - we add namespace separator at start, even when namespace is None (or ''), so we have a fully qualified namespaced id
    return DEF_mnamespace_separator + childid


def mnamespacedid_forpath(mnamespace, childid):
    """Combine parent and child mnamespace strings, suitable for use in a file path, where a mnamespace separator : would not be an allowed character."""
    if (not childid):
        childid = 'ANONYMOUS'
    # ATTN: TODO -- might we check if childid already has a namespace, and skip adding it if so?
    if (True and childid.find(DEF_mnamespace_separator)!=-1):
        # in this case we need to CHANGE the namespace separator to a PATH compatible namespace separator
        return childid.replace(DEF_mnamespace_separator,DEF_mnamespace_separator_forpath)
    if (mnamespace):
        return mnamespace + DEF_mnamespace_separator_forpath + childid
    # NOTE: IMPORTANT - we add namespace separator at start, even when namespace is None (or ''), so we have a fully qualified namespaced id
    return DEF_mnamespace_separator_forpath + childid


def lookup_mnamespaced_byid(id, mnamespace, thedict):
    if (not id.startswith(DEF_mnamespace_separator)):
        if (mnamespace):
            hashkey = mnamespace + DEF_mnamespace_separator + id
            if (hashkey in thedict):
                return thedict[hashkey]
        hashkey = DEF_mnamespace_separator + id
        if (hashkey in thedict):
            return thedict[hashkey]
    hashkey = id
    if (hashkey in thedict):
        return thedict[hashkey]
    # not found
    return None








def readfile_asjson(filepath, nicelabel):
    """
    Read a file and return json dictionary
    :return: EFailure on error
    """

    # mewlo imports
    from ..eventlog import mevent

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
    return (jsondict, None)








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






def resolve_expand_string(patternstring, replacementdict, mnamespace, depthcount=0):
    """Do recursive replacement in string with patterns."""
    #print "ATTN:DEBUG Asked to exp '"+patternstring+"' with :" + str(replacementdict)+" in mnamespace '{0}'".format(mnamespace)

    # mewlo imports
    from ..eventlog import mexceptionplus

    def resolve_expand_string_replacevar(match):
        """Recursive call to expand contents."""
        if (depthcount>99):
            # bailout of out-of-control recursion
            return retv
        # first lookup item, which will return None if not found
        replacedtext = lookup_mnamespaced_byid(match.group(1), mnamespace, replacementdict)
        if (replacedtext == None):
            raise Exception("Could not find a key during lookup_mnamespaced_byid for '{0}' (mnamespace '{1}') in alias replacement dictionary: {2}".format(match.group(1), mnamespace, replacementdict))
        # now recursively expand
        try:
            retv = resolve_expand_string(replacedtext, replacementdict, mnamespace, depthcount+1)
        except Exception as exp:
            mexceptionplus.reraiseplus(exp, "Failed to resolve_expandstring '{0}' (mnamespace '{1}') in alias replacement dictionary: {2}".format(replacedtext, mnamespace, replacementdict))
        return retv

    #if (patternstring == None):
    #    # error
    #    raise Exception("Replacement pattern string is None.");

    regexpat = r'\$\{([a-zA-Z0-9\_\-\:]+)\}'
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





def serialize_forstorage(obj):
    if (obj==None):
        return None
    return serialize_for_readability(obj)

def unserialize_fromstorage(serializedtext, defaultval=None):
    """Throw exception on error."""
    if (serializedtext==None or serializedtext==''):
        return defaultval
    obj = pickle.loads(str(serializedtext))
    return obj




def compare_versionstrings_isremotenewer(localversion, remoteversion):
    """
    Return true if remote version is newer.
    We expect versions to be of format ##.##.## where ## can be 0 leading or not, and .05 is same a .5, we integerize the #s
    :return: tuple (isremotenewer, failure)
    """
    # mewlo imports
    from ..eventlog import mevent

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
            return (True, None)
        elif (localpartval>remotepartval):
            # local version is newer (!)
            return False, mevent.EError("Locally installed version ({0}) is newer than remote version ({1}).".format(localversion,remoteversion))
        # a match for this part of version, keep checking

    # all parts in loop match, so now the only question is if there are more parts not yet parsed in remote
    if (len(localversionparts) < len(remoteversionparts)):
        # remote version is newer becase it has an additional part (i.e 2.0 < 2.0.000001
        return (True, None)

    # local version is same or newer
    return (False, None)




def strvalnone(val,noneval='n/a'):
    """Return string cast of a value or a default value if None."""
    if (val == None):
        return noneval
    return str(val)











# ATTN: todo move this somewhere
DEF_salthash_algorithm_u4s512v1 = 'u4s512v1'


def encode_hash_and_salt(plaintext):
    """Given plaintext, create a random-salted hash suitable for db storage; the salted+hashed string includes an algorithmstring to let us change algorithms later."""
    # use the latest algorithm (algorithm also covers how salt is chosen).
    algorithmstring = DEF_salthash_algorithm_u4s512v1
    # use a random salt
    salt = uuid.uuid4().hex
    # create the hash-salted string
    return encode_hash_and_salt_withparams(plaintext, algorithmstring, salt)


def encode_hash_and_salt_withparams(plaintext, algorithmstring, salt):
    """Given plaintext, create a salted hash suitable for db storage; the salted+hashed string includes an algorithmstring to let us change algorithms later."""
    if (salt == None):
        raise Exception("Blank salt not allowed.")
    if (algorithmstring==DEF_salthash_algorithm_u4s512v1):
        hashed_string = hashlib.sha512(plaintext + salt).hexdigest()
    else:
        if (algorithmstring == None):
            raise Exception("Algorithm string is not specified.")
        else:
            raise Exception("Unknown salthash algorithm specified: '{0}'.".format(algorithmstring))
    # the string is simple concatenation of params
    encodedstring = 'a={0}|s={1}|h={2}'.format(algorithmstring, salt, hashed_string)
    return encodedstring


def does_plaintext_rehash(plaintext, hashedchecktext):
    """We want to see if the plaintext matches the hashedchecktext."""
    # first sanity check against hashedchecktext
    if (hashedchecktext == None):
        return False
    # parse the parameters in the hashstring
    hashparams = parse_salthash_parameters(hashedchecktext)
    if ('a' not in hashparams):
        raise Exception("Algorithmstring value not specified in encoded salthash string.")
    if ('s' not in hashparams):
        raise Exception("Salt value not specified in encoded salthash string.")
    if ('h' not in hashparams):
        raise Exception("Hashed contents not specified in encoded salthash string.")
    algorithmstring = hashparams['a']
    salt = hashparams['s']
    # now recompute the hash
    plaintexthashed = encode_hash_and_salt_withparams(plaintext, algorithmstring, salt)
    # compare it to passed in hashed text (retrieved from db)
    # we could either compare plaintexthashed==hashedchecktext or hashparams['h']==parse_salthash_parameters(plaintexthashed)['h']
    # the only reason to do the latter is if additional keys might be added to the salthash string over time
    if (plaintexthashed == hashedchecktext):
        # it's a match
        return True
    # no match
    return False


def parse_salthash_parameters(hashedtext):
    """
    Parse the parameters in the hashstring which takes the form a={0}|s={1}|h={2}.
    Return dictionary of var=val.
    """
    paramdict = {}
    # first split on the |
    if (hashedtext != None):
        pipeparts = hashedtext.split('|')
        for pipepart in pipeparts:
            # split on v = val
            equalparts = pipepart.split('=',1)
            if (len(equalparts)==2):
                # parse it
                varpart = equalparts[0]
                valpart = equalparts[1]
                paramdict[varpart] = valpart
    # return it
    return paramdict







def nice_datestring(atime):
    """Return a nice string describing the datetime atime."""
    # ATTN: UNFINISHED -- we would like to say something like jan 1, 2010 at 5:4pm (3 weeks ago)
    localtime = time.localtime(atime)
    timestring = time.strftime('%A, %B %d, %Y at %I:%M %p',localtime)
    return timestring


def get_dbnowtime():
    """Return now time for database storage."""
    return time.time()


def convert_list_to_id_indexed_dict(objlist):
    """Convert a list of objects to a dictionary indexed by obj.id."""
    indexeddict = {}
    for obj in objlist:
        indexeddict[obj.id] = obj
    return indexeddict


def convert_list_to_attribute_indexed_dict(objlist, attributename):
    """Convert a list of objects to a dictionary indexed by obj.id."""
    indexeddict = {}
    for obj in objlist:
        attributeval = getattr(obj, attributename)
        indexeddict[attributeval] = obj
    return indexeddict





def canonicalize_filepath(filepath):
    """Convert \ to / and remove trailing /"""
    # ATTN: UNFINISHED
    return os.path.normpath(filepath)



























def copy_tree_withcallback(src, dst, preserve_mode=1, preserve_times=1,
              preserve_symlinks=0, update=0, verbose=1, dry_run=0, callbackfp=None):
    """
    Improved version of Python's distutils.file_util.copy_tree
    With support for a callback evaluating files before operations.

    Copy an entire directory tree 'src' to a new location 'dst'.

    Both 'src' and 'dst' must be directory names.  If 'src' is not a
    directory, raise DistutilsFileError.  If 'dst' does not exist, it is
    created with 'mkpath()'.  The end result of the copy is that every
    file in 'src' is copied to 'dst', and directories under 'src' are
    recursively copied to 'dst'.  Return the list of files that were
    copied or might have been copied, using their output name.  The
    return value is unaffected by 'update' or 'dry_run': it is simply
    the list of all files under 'src', with the names changed to be
    under 'dst'.

    'preserve_mode' and 'preserve_times' are the same as for
    'copy_file'; note that they only apply to regular files, not to
    directories.  If 'preserve_symlinks' is true, symlinks will be
    copied as symlinks (on platforms that support them!); otherwise
    (the default), the destination of the symlink will be copied.
    'update' and 'verbose' are the same as for 'copy_file'.
    """
    from distutils.file_util import copy_file
    from distutils.dir_util import mkpath
    from distutils.errors import DistutilsFileError

    if not dry_run and not os.path.isdir(src):
        raise DistutilsFileError(
              "cannot copy tree '%s': not a directory" % src)
    try:
        names = os.listdir(src)
    except os.error as e:
        (errno, errstr) = e
        if dry_run:
            names = []
        else:
            raise DistutilsFileError(
                  "error listing files in '%s': %s" % (src, errstr))

    if not dry_run:
        mkpath(dst, verbose=verbose)

    outputs = []

    for n in names:
        src_name = os.path.join(src, n)
        dst_name = os.path.join(dst, n)

        (flag_docopy, src_name, dst_name) = callbackfp(src_name, dst_name)
        if (not flag_docopy):
            continue

        if n.startswith('.nfs'):
            # skip NFS rename files
            continue

        if preserve_symlinks and os.path.islink(src_name):
            link_dest = os.readlink(src_name)
            if verbose >= 1:
                log.info("linking %s -> %s", dst_name, link_dest)
            if not dry_run:
                os.symlink(link_dest, dst_name)
            outputs.append(dst_name)

        elif os.path.isdir(src_name):
            outputs.extend(
                copy_tree_withcallback(src_name, dst_name, preserve_mode,
                          preserve_times, preserve_symlinks, update,
                          verbose=verbose, dry_run=dry_run, callbackfp=callbackfp))
        else:
            copy_file(src_name, dst_name, preserve_mode,
                      preserve_times, update, verbose=verbose,
                      dry_run=dry_run)
            outputs.append(dst_name)

    return outputs



def makedirectorypath(dirpath):
    """Just a thin wrapper around mkpath."""
    from distutils.dir_util import mkpath
    retv = mkpath(dirpath)
    return retv





def build_ahref_link(linktext, linkargs, url):
    """Build an a href link given text and args."""
    extrataghtml = build_extrataghtml(linkargs)
    htmltext = '<a href="{0}"{1}>{2}</a>'.format(url,extrataghtml,linktext)
    return htmltext

def build_extrataghtml(tagdict):
    """Build a text string of tag assignments for within an html element."""
    htmltext = ''
    if (tagdict):
        for (key,val) in tagdict.iteritems():
            htmltext += ' {0}="{1}"'.format(key,val)
    return htmltext










def set_object_properties_from_dict(obj, propdict, knownprops = {}):
    """Set any properties from from dictionary..."""
    for (key,val) in propdict.iteritems():
        if ((key in knownprops) or (hasattr(obj,key))):
            setattr(obj, key, val)




def dict_to_headitem(headitem_dict):
    """Make a head link from dictionary."""
    headtypes_openclose = ['script']
    headitem_typestr = headitem_dict['_type']
    rethtml ='<{0}'.format(headitem_typestr)
    for key,val in headitem_dict.iteritems():
        if (not key.startswith('_')):
            rethtml += ' {0}="{1}"'.format(key,val)
    # optional inner contents between tags
    if ('_inner' in headitem_dict):
        innercontents = headitem_dict['_inner']
    else:
        innercontents = ''
    #
    if (innercontents or (headitem_typestr in headtypes_openclose)):
        rethtml +='>{0}</{1}>'.format(innercontents,headitem_typestr)
    else:
        rethtml +=' />'

    return rethtml


def headitems_tohtml(headitems):
    """Return html for headlinks to put in head section."""
    reth = ''
    for headitem in headitems:
        reth += headitem + '\n'
    return reth



def isabsoluteurl(urlpath):
    """Return True if urlpath is already an absolute path (starting with http)."""
    if (urlpath.startswith('http') or urlpath.startswith('//')):
        return True
    return False