"""
msitemanager.py
This file contains classes to handle Mewlo site manager class.
"""


# mewlo imports
import mrequest
import mglobals

# helper imports
from helpers.event.event import Event, EventList

# python imports
from datetime import datetime









class MewloSiteManager(object):
    """
    The MewloManager class holds a collection of Mewlo "sites", which can handle incoming requests.
    Typically, you would have only one single site running from your web server, but there may be times when you want to server multiple sites from a single instantiation running off a single port.
    When supporting multiple sites, the sites are completely independent of one another, and must have completely separate uri prefixes.  They share nothing.
    """


    def __init__(self, debugmode, siteclass=None):
        # the collection of sites that this manager takes care of
        self.sites = list()
        self.prepeventlist = EventList()
        # if a siteclass was pased, create it
        if (siteclass!=None):
            self.create_add_site_from_class(siteclass, debugmode)


    def add_site(self, site):
        """Add a site to our list of managed sites."""
        self.sites.append(site)





    def startup(self):
        """Ask all children sites to 'startup'."""
        for site in self.sites:
            site.startup(self.prepeventlist)
        return self.prepeventlist

    def shutdown(self):
        """Ask all children sites to 'shutdown'."""
        for site in self.sites:
            site.shutdown(self.prepeventlist)
        return self.prepeventlist






    def create_add_site_from_class(self, siteclass, debugmode):
        """Instatiate a site class and set it to be owned by use."""
        # instantiate the site
        site = siteclass(debugmode)
        # tell the site we are the sitemanager for it
        site.set_sitemanager(self)
        # early setup stuff for site
        site.setup_early()
        # take ownership of the site
        self.add_site(site)
        # retuen the newly created site
        return site









    def debugmessage(self, astr):
        """
        Display a simple debug message with date+time to stdout.
        ATTN: We probably want to remove this later.
        """

        nowtime = datetime.now()
        outstr = "MEWLODEBUG [" + nowtime.strftime("%B %d, %Y at %I:%M%p") + "]: " + astr
        print outstr



    def test_submit_path(self, pathstr):
        """Simulate the submission of a url."""

        outstr = ""
        outstr += "Testing submission of url: " + pathstr + "\n"
        # generate request and debug it
        request = mrequest.MewloRequest.createrequest_from_pathstring(pathstr)
        outstr += request.dumps()
        # generate response and debug it
        self.process_request(request)
        outstr += request.response.dumps()
        # return debug text
        return outstr




    def create_and_start_webserver_wsgiref(self, portnumber=8080):
        """Create a wsgiref web server and begin serving requests."""

        # see http://lucumr.pocoo.org/2007/5/21/getting-started-with-wsgi/
        from wsgiref.simple_server import make_server
        srv = make_server('localhost', portnumber, self.wsgiref_callback)
        srv.serve_forever()




    def process_request(self, request):
        """Process a request by handing it off to all of our child sites in turn until we find one that will handle it."""

        # first do any pre-processing on the request
        self.preprocess_request(request)

        # walk through the site list and let each site take a chance at processing the request
        for site in self.sites:
            # in an early version of mewlo, we used no globals and passed the site around through function calls
            # however, because we don't practically expect to be handling multiple sites, and to ease code cleanliness,
            # we now use a site global and expect to process only one request at a time.
            # We can however, kludge our way to supporting multiple sites under the manager by setting the global per request
            # ATTN: TODO - use thread locals for this?
            # Set global variable indicating which site is processing this request
            mglobals.set_mewlosite(site)
            #
            ishandled = site.process_request(request)
            if (ishandled):
                # ok this site handled it
                break

        if (not ishandled):
            # no site handled it, so this is an error
            request.response.add_status_error(404, "Page not found or supported on any site: '{0}'.".format(request.get_path()))

        # return response
        return True



    def wsgiref_callback(self, environ, start_response):
        """Receive a callback from wsgi web server.  We process it and then send response."""

        outstr = "wsgiref_callback:\n"
        outstr += " " + str(environ) + "\n"
        outstr += " " + str(start_response) + "\n"
        # debug display?
        if (False):
            self.debugmessage(outstr)
        # create request
        request = mrequest.MewloRequest.createrequest_from_wsgiref_environ(environ)
        # get response
        ishandled = self.process_request(request)
        # process response
        return request.response.start_and_make_wsgiref_response(start_response)



    def preprocess_request(self, request):
        """Pre-process and parse the request.  Here we might add stuff to it before asking child sites to look at it."""
        request.preprocess()



    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = " "*indent + "MewloSiteManager reporting in.\n"
        outstr += self.prepeventlist.dumps(indent+1)
        outstr += self.debug_sites(indent+1)
        return outstr


    def debug_sites(self, indent=1):
        """Debug helper; return string with recursive debug info from child sites."""
        outstr = " "*indent + "Sites: "
        if (len(self.sites) == 0):
            outstr += "None.\n"
        else:
            outstr += "\n"
        for site in self.sites:
            outstr += site.dumps(indent+1) + "\n"
        return outstr


