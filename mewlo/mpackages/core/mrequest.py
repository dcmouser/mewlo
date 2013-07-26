# mrequest.py
# This file contains classes to support web server requests

from mreply import MewloReply





class MewloRequest(object):
    """
    The MewloRequest class handles a web server request
    """

    def __init__(self, in_sitemanager):
        # init -- note that request contains reference to the site manager (and site it's assigned to), so that it contains all info needed for processing and is the only thing we need to pass around
        self.sitemanager = in_sitemanager
        self.site = None
        self.url = ""
        # note that a request contains a reply, to be filled in during processing of request
        self.reply= MewloReply(self)


    def set_url(self, in_url):
        self.url = in_url






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
        # return it
        return request
