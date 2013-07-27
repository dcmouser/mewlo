# mrequest.py
# This file contains classes to support web server requests

# mewlo stuff
from mresponse import MewloResponse

# this version uses werkzeug to do heavy lifting
from werkzeug.wrappers import Request
from werkzeug.test import create_environ



class MewloRequest(object):
    """
    The MewloRequest class handles a web server request
    """

    def __init__(self, in_sitemanager):
        # init -- note that request contains reference to the site manager (and site it's assigned to), so that it contains all info needed for processing and is the only thing we need to pass around
        self.sitemanager = in_sitemanager
        self.site = None
        self.wreq = None
        # note that a request contains a response, to be filled in during processing of request
        self.response = MewloResponse(self)


    def get_path(self):
        return self.wreq.path

    def get_environ(self):
        return self.wreq.environ





    def make_werkzeugrequest(self, wsgiref_environ):
        self.wreq = Request(wsgiref_environ)
        return self.wreq









    def debug(self, indentstr=""):
        outstr = indentstr+" MewloRequest reporting in:\n"
        outstr += indentstr+"  URL: "+self.get_path()+"\n"
        return outstr












    @classmethod
    def createrequest_from_pathstring(cls, sitemanager, pathstr):
        # simulate werkzeug call environ
        env = create_environ(pathstr, "http://localhost"+pathstr)
        # create request
        return cls.createrequest_from_wsgiref_environ(sitemanager, env)


    @classmethod
    def createrequest_from_wsgiref_environ(cls, sitemanager, wsgiref_environ):
        # create request
        request = MewloRequest(sitemanager)
        # now werkzeug does the work
        request.make_werkzeugrequest(wsgiref_environ)
        # return it
        return request
