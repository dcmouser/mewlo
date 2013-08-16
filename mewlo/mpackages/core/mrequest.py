"""
mrequest.py
This file contains classes to support web server requests
"""


# mewlo imports
from mresponse import MewloResponse

# werkzeug imports
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
        self.route = None
        # note that a request contains a response, to be filled in during processing of request
        self.response = MewloResponse(self)



    def get_path(self):
        return self.wreq.path

    def get_environ(self):
        return self.wreq.environ


    def set_route_parsedargs(self, parsedargs):
        self.parsedargs = parsedargs
    def get_route_parsedargs(self):
        return self.parsedargs

    def set_matched(self, route, site):
        self.route = route
        self.site = site


    def get_route(self):
        return self.route
    def get_site(self):
        return self.site



    def make_werkzeugrequest(self, wsgiref_environ):
        """Create a werkzeug request from the environment and attach it to us."""
        self.wreq = Request(wsgiref_environ)
        return self.wreq



    def preprocess(self):
        """Do any preprocessing of the request.  Base class does nothing here."""
        pass



    def logevent(self, mevent):
        """Shortcut helper just sends the log message to the site to handle, after adding the request to the log function call being invoked."""
        # add request field (if it wasn't already set in mevent)
        missingfields = { 'request': self }
        mevent.mergemissings(missingfields)
        # add it via site
        self.site.logevent(mevent)



    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = " "*indent + "MewloRequest reporting in:\n"
        outstr += " "*indent + " URL: " + self.get_path() + "\n"
        return outstr




    @classmethod
    def createrequest_from_pathstring(cls, pathstr):
        """Create a simulated web request from a path string, using werkzeug helper function."""
        env = create_environ(pathstr, 'http://localhost'+pathstr)
        # create request
        return cls.createrequest_from_wsgiref_environ(env)



    @classmethod
    def createrequest_from_wsgiref_environ(cls, wsgiref_environ):
        """Helper function to create a simulated web request from a path string, using werkzeug helper function."""
        # create request
        request = MewloRequest()
        # now werkzeug does the work
        request.make_werkzeugrequest(wsgiref_environ)
        # return it
        return request



