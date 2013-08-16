"""
misc.py
This module contains misclenaeous helper functions.
"""


# helper imports
from event.event import EFailure, EException




def readfile_asjson(filepath, nicelabel):
    """
    Read a file and return json dictionary
    :return: EFailure on error
    """

    # python libraries
    import json

    # make sure filename is nonblanck
    if (filepath == ""):
        return None, EFailure(nicelabel+" has blank info file path")

    # open the file and load into a string
    try:
        # open file for reading, and read it into string
        file = open(filepath, 'r')
    except Exception as exp:
        return None, EException("Failed to open '{0}' from path '{1}'.".format(nicelabel,filepath), exp=exp, flag_traceback=False )

    # read the file
    try:
        jsonstr = file.read()
    except Exception as exp:
        return None, EException("Opened but failed to read contents of '{0}' from path '{1}'.".format(nicelabel,filepath), exp=exp, flag_traceback=False )
    finally:
        file.close()

    # parse string as json
    try:
        jsondict = json.loads(jsonstr)
    except Exception as exp:
        return None, EException("Syntax error parsing json code in '{0}' from file '{1}'.".format(nicelabel,filepath), exp=exp, flag_traceback=True)

    # success
    return jsondict, None


