"""
mrequest.py
This file contains classes to support web server requests.
For now our requests are just lightly wrapped werkzeug requests.
"""


# mewlo imports
import mresponse
from ..user import muser

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
        self.siteurlpath = None
        #
        self.session = None
        self.user = None
        # note that a request contains a response, to be filled in during processing of request
        self.response = mresponse.MewloResponse(self)





    # accessors

    def get_sitecomp_usermanager(self):
        return self.mewlosite.comp('usermanager')

    def sitecomp_sessionmanager(self):
        return self.mewlosite.comp('sessionmanager')

    def get_urlpath(self):
        """Return the url path of the request.
        This value is cached, and represents the relative path within the 'site' configuration, excluding any site prefix path.
        This function is called after preprocessing a reqest and is the call you would use in almost all cases when examining path."""
        if (self.siteurlpath != None):
            return self.siteurlpath
        return self.get_urlpath_original()

    def set_urlpath(self,val):
        """Set the cached url parth ed url for this request, called after stripping off any site prefix part of the path."""
        self.siteurlpath = val

    def set_route_parsedargs(self, parsedargs):
        """Store parsed args for the request."""
        self.parsedargs = parsedargs
    def get_route_parsedargs(self):
        """Get previously parsed args for the request."""
        return self.parsedargs

    def set_matched(self, route, mewlosite):
        """Set values to track which route this request matched and is being processed by."""
        self.route = route
        self.mewlosite = mewlosite

    def get_route(self):
        """Get the route that this request was matched against and processed by."""
        return self.route

    def get_route_parsedarg(self, argname, defaultval):
        """Accessor."""
        if (argname in self.parsedargs):
            return self.parsedargs[argname]
        return defaultval













    # werkzeug-related thin accessors

    def get_urlpath_original(self):
        """Get full true original path of request, without any get arguements."""
        return self.wreq.path

    def get_fullurlpath_original(self):
        """Get full true original url path of request, including any get arguements."""
        return self.wreq.full_path

    def get_environ(self):
        """Get werkzeug environment for request.  This is used when calling into some werkzeug functions (see wresp() function in mrespoonse.py)."""
        return self.wreq.environ

    def get_remote_addr(self):
        """Get ip of client in request."""
        return self.wreq.remote_addr

    def get_postdata(self):
        """
        Get form post data (dictionary)
        return None if there is none.
        """
        if (not self.get_ispostmethod()):
            # the form data wasn't posted (gett'd?), so we disallow
            return None
        return self.wreq.form

    def get_cookieval(self,cookiename):
        """Return cookie from client browser request."""
        return self.wreq.cookies.get(cookiename)

    def delete_cookie_byname(self,cookiename):
        """Return cookie from client browser request."""
        return self.wreq.delete_cookie(cookiename)

    def get_ispostmethod(self):
        """Return True if request was submitting data with POST method."""
        return (self.wreq.method == 'POST')

    def make_werkzeugrequest(self, wsgiref_environ):
        """Create a werkzeug request from the environment and attach it to us."""
        self.wreq = Request(wsgiref_environ)
        return self.wreq

























    # lazy stuff

    def get_session(self, flag_makesessionifnone):
        """Lazy create or load session object."""
        if (self.session == None):
            self.session = self.sitecomp_sessionmanager().get_session(self, flag_makesessionifnone)
        return self.session

    def save_session_ifdirty(self):
        """Lazy save session data IFF it needs it; this will also set client browser cookie for session."""
        if (self.session == None):
            return
        if (self.session.get_isdirty()):
            # session has changes to save, so save it
            #print "ATTN: SAVING SESSION."
            self.session.save()
            # and make sure the user gets a cookie pointing to this session
            self.response.set_cookieval(self.sitecomp_sessionmanager().get_sessionid_cookiename(), self.session.hashkey)
        # shall we autosave session user?
        # ATTN: i don't know how smart db is about avoiding resave if nothing changed
        # ATTN: TODO avoid trying to save if not diry
        user = self.get_user()
        if (user != None):
            user.save()

    def get_user(self):
        """Lazy get the user object of the requesting user.
        This will trigger session creation, then session lookup of user if need be."""
        if (self.user == None):
            # ATTN: TODO - investigate and think about this; if we don't pass true here then sessions get forgetten; it's not clear if we need a fast way to check if user logged in without triggering full session creation
            session = self.get_session(True)
            if (session != None):
                self.user = session.get_user()
        return self.user

    def set_user(self, userobject):
        """Set the user object of the requesting user.
        This will trigger session creation if need be."""
        self.get_session(True).set_user(userobject)
        self.user = userobject

    def get_user_or_maketemporaryguest(self):
        """Lazy get the user object of the requesting user.
        This will trigger session creation, then session lookup of user if need be."""
        if (self.user == None):
            # quick temporary user, without causing session creation
            user = self.get_user()
            if (user == None):
                user = self.get_sitecomp_usermanager().getmake_guestuserobject()
            return user
        return self.user


    def clearloggedinuser(self):
        """Clear the loggedin user (performed on a logout)."""
        self.set_user(None)



    def clearusersession(self):
        """Remove any session id for the user, so they will be a stranger on next request."""
        session = self.get_session(False)
        #return
        if (session != None):
            #session.flush_toupdate()
            session.delete()
        self.session = None



















    def preprocess(self):
        """Do any preprocessing of the request.  Base class does nothing here."""
        pass



    def logevent(self, event):
        """Shortcut helper just sends the log message to the site to handle, after adding the request to the log function call being invoked."""
        # add it via site
        self.mewlosite.logevent(event,request = self)



    def preprocess_siteprefix(self, siteprefix):
        """Check if request matches siteprefix, if so, set self.siteurlpath and return True, otherwise clear siteurlpath return False."""
        requestpath = self.get_urlpath_original()
        if (requestpath.startswith(siteprefix)):
            # it matches, strip prefix and set siteurlpath
            self.set_urlpath(requestpath[len(siteprefix):])
            return True
        # does not match
        #print "Failed to match request '{0}' against prefix of '{1}'.".format(siteprefix,requestpath)
        self.set_urlpath(None)
        return False









    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = " "*indent + "MewloRequest reporting in:\n"
        outstr += " "*indent + " URL: " + self.get_urlpath_original() + "\n"
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






