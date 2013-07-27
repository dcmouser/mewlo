# mrequest.py
# This file contains classes to support web server requests

# mewlo stuff
from mresponse import MewloResponse

# this version uses werkzeug to do heavy lifting
from werkzeug.wrappers import Request




class MewloRequest(object):
    """
    The MewloRequest class handles a web server request
    """

    def __init__(self, in_sitemanager):
        # init -- note that request contains reference to the site manager (and site it's assigned to), so that it contains all info needed for processing and is the only thing we need to pass around
        self.sitemanager = in_sitemanager
        self.site = None
        self.wreq = None
        self.url = None
        # note that a request contains a response, to be filled in during processing of request
        self.response = MewloResponse(self)


    def set_url(self, in_url):
        self.url = in_url
    def get_url(self):
        return self.url

    def get_environ(self):
        return self.wreq.environ





    def make_werkzeugrequest(self,wsgiref_environ):
        self.wreq = Request(wsgiref_environ)
        self.store_wreq_values()
        return self.wreq

    def store_wreq_values(self):
        self.url = self.wreq.base_url







    def debug(self, indentstr=""):
        outstr = indentstr+" MewloRequest reporting in:\n"
        outstr += indentstr+"  URL: "+self.url+"\n"
        return outstr












    @classmethod
    def createrequest_from_urlstring(cls, sitemanager, url):
        # create request
        request = MewloRequest(sitemanager)
        # set values
        request.set_url(url)
        # return it
        return request


    @classmethod
    def createrequest_from_wsgiref_environ(cls, sitemanager, wsgiref_environ):
        # create request
        request = MewloRequest(sitemanager)
        # now werkzeug does the work
        request.make_werkzeugrequest(wsgiref_environ)
        # return it
        return request
