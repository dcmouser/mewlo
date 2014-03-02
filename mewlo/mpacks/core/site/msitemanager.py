"""
msitemanager.py
This file contains classes to handle Mewlo site manager class.
"""


# mewlo imports
from ..reqresp import mrequest
from .. import mglobals

# helper imports
from ..eventlog import mevent

# python imports
from datetime import datetime









class MewloSiteManager(object):
    """
    The MewloManager class holds a collection of Mewlo "sites", which can handle incoming requests.
    Typically, you would have only one single site running from your web server, but there may be times when you want to server multiple sites from a single instantiation running off a single port.
    When supporting multiple sites, the sites are completely independent of one another, and must have completely separate uri prefixes.  They share nothing.
    """


    def __init__(self, debugmode, siteclass=None, commandlineargs=None):
        # the collection of sites that this manager takes care of
        self.sites = list()
        self.prepeventlist = mevent.EventList()
        self.commandlineargs = commandlineargs
        self.debugmode = debugmode
        # if a siteclass was pased, create it
        if (siteclass!=None):
            self.create_add_site_from_class(siteclass)


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






    def create_add_site_from_class(self, siteclass):
        """Instatiate a site class and set it to be owned by use."""
        # instantiate the site
        site = siteclass(self.debugmode, self.commandlineargs)
        # early setup stuff for site
        site.setup_early()
        # tell the site we are the sitemanager for it
        site.set_sitemanager(self)
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
            request.response.add_status_error(404, "Page not found or supported on any site: '{0}'.".format(request.get_urlpath_original()))

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

        # write out any pending session data that needs saving
        request.save_session_ifdirty()

        # finalize response if it needs it
        request.response.finalize_response()

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
        outstr += " "*indent + "MewloSiteManager finished report.\n"
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







    def is_readytoserve(self):
        """Check if there were any site prep errors, OR if any packs report they are not ready to run (need update, etc.)."""
        isreadytoserve = True
        # check sites
        for site in self.sites:
            if (not site.is_readytoserve()):
                isreadytoserve = False
        # any fatal errors
        if (self.has_preparationerrors()):
            isreadytoserve = False
        # it's ready?
        return isreadytoserve


    def has_preparationerrors(self):
        """Return true if there were fatal preparation errors."""
        if (self.prepeventlist.count_errors() > 0):
            return True
        return False













    def updatecheck(self):
        """
        Check all packs for updates.  The packs themselves will store details about update check results.
        Note this covers not just web updates available, but database updates needed.
        """
        for site in self.sites:
            site.updatecheck()


    def updaterun(self):
        """
        Check all packs for updates.  The packs themselves will store details about update check results.
        Note this covers not just web updates available, but database updates needed.
        """
        for site in self.sites:
            site.updaterun()


    def get_allpack_events(self):
        """
        Get combined eventlist for all packs on all sites
        """
        alleventlist = mevent.EventList()
        for site in self.sites:
            siteeventlist = site.get_allpack_events()
            alleventlist.appendlist(siteeventlist)
        return alleventlist






















    @classmethod
    def do_main_commandline_startup(cls, siteclass, parser = None):
        """
        Shortcut helper function to create a sitemanager and site and parse main commandline options.
        :return: tuple (args, sitemanager)
        """

        # create commandline parser if none passed
        if (parser == None):
            import argparse
            parser = argparse.ArgumentParser()

        # add standard args
        parser.add_argument("-d", "--debug", help="run in debug mode (combine with others)",action="store_true", default=False)
        parser.add_argument("-s", "--runserver", help="run the web server",action="store_true", default=False)
        parser.add_argument("-uc", "--updatecheck", help="check for updates",action="store_true", default=False)
        parser.add_argument("-ur", "--updaterun", help="perform updates",action="store_true", default=False)
        parser.add_argument("-c", "--config", help="overide config set name",action="store")
        args = parser.parse_args()

        # Create a site manager and ask it to instantiate a site of the class we specify
        sitemanager = MewloSiteManager(args.debug, siteclass, args)

        # early stuff
        sitemanager.do_main_commandline_early()

        # return it
        return (args, sitemanager)



    def do_main_commandline_early(self):
        """Commandline early default processing."""

        # startup sites - this will generate any preparation errors
        self.startup()

        # some other flags
        flag_updates_check = self.commandlineargs.updatecheck
        flag_updates_run = self.commandlineargs.updaterun

        # update checking?
        if (flag_updates_check):
            self.updatecheck()
            print "Debugging update check results:"
            eventlist = self.get_allpack_events()
            print eventlist.dumps()

        # update running
        if (flag_updates_run):
            self.updaterun()
            print "Debugging update run results:"
            eventlist = self.get_allpack_events()
            print eventlist.dumps()

        # display some debug info
        if (self.debugmode):
            print "Debugging site manager."
            print self.dumps()




    def do_main_commandline_late(self):
        """Commandline late default processing."""

        # some things we can only do if everything went well enough to serve
        if (self.is_readytoserve()):
            # run server?
            if (self.commandlineargs.runserver):
                # start serving the web server and process all web requests
                print "Starting web server."
                self.create_and_start_webserver_wsgiref()
        else:
            print "Sitemanager reports it is not ready to run:"
            print self.prepeventlist.dumps()

        # we are responsible for shutting down
        print "Shutting down."
        self.shutdown()














