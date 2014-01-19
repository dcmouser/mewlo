"""
mrequest.py
This file contains classes to support web server requests.
For now our requests are just lightly wrapped werkzeug requests.
"""


# mewlo imports
import mresponse
from .. import mglobals

# werkzeug imports
from werkzeug.wrappers import Request
from werkzeug.test import create_environ




class MewloRequest(object):
    """
    The MewloRequest class handles a web server request
    Note that our request class contains a reference to the response object.
    """

    def __init__(self):
        # for now we use werkzeug to do our heavy lifting
        self.wreq = None
        # misc from request
        self.parsedargs = None
        self.route = None
        self.mewlosite = None
        self.sitepath = None
        # note that a request contains a response, to be filled in during processing of request
        self.response = mresponse.MewloResponse(self)



    def get_path(self):
        return self.wreq.path

    def get_sitepath(self):
        if (self.sitepath != None):
            return self.sitepath
        return self.get_path()

    def set_sitepath(self,val):
        self.sitepath = val

    def get_environ(self):
        return self.wreq.environ


    def set_route_parsedargs(self, parsedargs):
        self.parsedargs = parsedargs
    def get_route_parsedargs(self):
        return self.parsedargs

    def set_matched(self, route, mewlosite):
        self.route = route
        self.mewlosite = mewlosite

    def get_route(self):
        return self.route





    def make_werkzeugrequest(self, wsgiref_environ):
        """Create a werkzeug request from the environment and attach it to us."""
        self.wreq = Request(wsgiref_environ)
        return self.wreq



    def preprocess(self):
        """Do any preprocessing of the request.  Base class does nothing here."""
        pass



    def logevent(self, event):
        """Shortcut helper just sends the log message to the site to handle, after adding the request to the log function call being invoked."""
        # add it via site
        self.mewlosite.logevent(event,request = self)



    def preprocess_siteprefix(self, siteprefix):
        """Check if request matches siteprefix, if so, set self.sitepath and return True, otherwise clear sitepath return False."""
        requestpath = self.get_path()
        if (requestpath.startswith(siteprefix)):
            # it matches, strip prefix and set sitepath
            self.set_sitepath(requestpath[len(siteprefix):])
            return True
        # does not match
        #print "Failed to match request '{0}' against prefix of '{1}'.".format(siteprefix,requestpath)
        self.set_sitepath(None)
        return False









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



