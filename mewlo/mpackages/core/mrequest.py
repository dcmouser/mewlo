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

    def __init__(self):
        # init
        self.site = None
        # for now we use werkzeug to do our heavy lifting
        self.wreq = None
        # misc from request
        self.parsedargs = None
        self.matchedroute = None
        # note that a request contains a response, to be filled in during processing of request
        self.response = MewloResponse(self)



    def get_path(self):
        return self.wreq.path

    def get_environ(self):
        return self.wreq.environ


    def set_route_parsedargs(self, in_parsedargs):
        self.parsedargs = in_parsedargs
    def get_route_parsedargs(self):
        return self.parsedargs

    def set_matched(self, route, site):
        self.matchedroute = route
        self.matchedsite = site

    def get_matchedroute(self):
        return self.matchedroute
    def get_matchedsite(self):
        return self.matchedsite






    def make_werkzeugrequest(self, wsgiref_environ):
        self.wreq = Request(wsgiref_environ)
        return self.wreq





    def preprocess(self):
        # any preprocessing to do after request is built?
        pass





    def debug(self, indentstr=""):
        outstr = indentstr+" MewloRequest reporting in:\n"
        outstr += indentstr+"  URL: "+self.get_path()+"\n"
        return outstr












    @classmethod
    def createrequest_from_pathstring(cls, pathstr):
        # simulate werkzeug call environ
        env = create_environ(pathstr, "http://localhost"+pathstr)
        # create request
        return cls.createrequest_from_wsgiref_environ(env)


    @classmethod
    def createrequest_from_wsgiref_environ(cls, wsgiref_environ):
        # create request
        request = MewloRequest()
        # now werkzeug does the work
        request.make_werkzeugrequest(wsgiref_environ)
        # return it
        return request

