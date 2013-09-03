"""
setuptoolshelpers.py

This file defines helper functions for the mewlo setuptools based test plugin, which is used to test one way of autodiscovering plugins for mewlo.

"""




def shelp_readfile_asjson(filepath):
    """
    Read a file and return json dictionary
    :return: jsondictionary_of_readfile
    :raises: exception on error parsing or reading file
    """

    # python libraries
    import json


    # open the file and load into a string
    try:
        # open file for reading, and read it into string
        file = open(filepath, 'r')
    except Exception as exp:
        raise

    # read the file
    try:
        jsonstr = file.read()
    except Exception as exp:
        raise
    finally:
        file.close()

    # parse string as json
    try:
        jsondict = json.loads(jsonstr)
    except Exception as exp:
        raise

    # success
    return jsondict




def dvalordef(adict, akey, adefault=None):
    if (akey in adict):
        return adict[akey]
    return adefault


