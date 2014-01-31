"""
webhelp.py
This module contains misclenaeous helper functions related to online web functions
"""


# helper imports
from ..eventlog import mevent
from ..eventlog import mexceptionplus
from misc import readfile_asjson

# python imports
import requests





def download(url):
    """Download a file from a url, return the file."""
    r = requests.get(url)
    return r


def download_file_asstring(url):
    """Download a file from a url, return as string."""
    r = download(url)
    return r.text


def download_file_as_jsondict(url):
    """
    Download a file from a url, return it as a parsed json dictionary.
    :return: tuple (downloadedfilepath, failure)
    """
    try:
        r = download(url)
        # print "ATTN: DEBUG downloaded {0} as: ".format(url) + str(r)
        rjson = r.json()
        return rjson, None
    except Exception as exp:
        return None, mevent.EException("Error downloading and parsing json file from '{0}'.".format(url), exp=exp, flag_traceback=True)



def download_file_to_file(url, targetfilepath):
    """
    Download a remote file and save it in a local file.
    :return: tuple (downloadedfilepath, failure)
    """
    # open output file
    try:
        with open(targetfilepath, 'wb') as handle:
            # request download file
            request = requests.get(url, stream=True)
            # now loop and write it out
            for block in request.iter_content(1024):
                if not block:
                    break
                handle.write(block)
            # success
            return targetfilepath, None
        # failed
        return None, mevent.EFailure('Failed to open target file for download ({0}).'.format(targetfilepath))
    except Exception as exp:
        return None, mevent.EException("Error downloading file from '{0}' to save to '{1}'.".format(url,targetfilepath), exp=exp, flag_traceback=True)

