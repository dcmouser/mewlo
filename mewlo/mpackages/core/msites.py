# msites.py
# This file contains classes to handle Mewlo sites and site manager.

# global constants
DefMewlo_BasePackage_subdirlist = ["mpackages"]



# Import the mewlo modules we need from the mpackages/core directory
import mewlo
from msettings import MewloSettings
from mpackage import MewloPackageManager
from mrequest import MewloRequest
from mresponse import MewloResponse
from mroutemanager import MewloRouteGroup

# helpers
from mewlo.mpackages.core.helpers.eventtracker import EventTracker
from mewlo.mpackages.core.helpers.logger.logger import LogManager, Logger, LogMessage
from mewlo.mpackages.core.mewlologger import MewloLogMessage

# python libs
import os
from datetime import datetime, date, time










class MewloSite(object):
    """
    The MewloSite class represents a single "site" that handles requests.
    Typically you will only have one site running.
    """

    # class constants
    DEF_SECTION_config = "config"
    DEF_CONFIGVAR_pkgdirimps_sitempackages = "pkgdirimps_sitempackages"
    DEF_CONFIGVAR_controllerroot = "controllerroot"
    DEF_CONFIGVAR_urlprefix = "urlprefix"



    def __init__(self, sitemodulename, sitename=None):
        # initialize settings
        if (sitename==None):
            sitename = self.__class__.__name__
        self.sitename = sitename
        self.sitemanager = None
        self.controllerroot = None
        # create site settings
        self.sitesettings = MewloSettings()
        # collection of mewlo addon packages
        self.packagemanager = MewloPackageManager(self)
        # route manager
        self.routes = MewloRouteGroup()
        # log manager
        self.logmanager = LogManager(self)
        # record package of the site for relative imports
        self.sitemodulename = sitemodulename



    def get_controllerroot(self):
        return self.controllerroot
    def get_sitename(self):
        return self.sitename
    def get_id(self):
        # generic get_id function used in lots of places to help display debug info
        return self.get_sitename()



    def merge_settings(self, settings):
        """Merge in some settings to our site settings."""
        self.sitesettings.merge_settings(settings)



    def create_and_prepare_standalone_sitemanager(self):
        """Create and prepare a single-site sitemananger specifically for this site"""
        # create site manager
        mysitemanager = MewloSiteManager()
        # set it to be our site manager
        self.set_and_add_sitemanager(mysitemanager)
        # ask it to prepare for work
        errors = self.sitemanager.prepare()
        # return the site manager created
        return self.sitemanager



    def set_and_add_sitemanager(self, sitemanager):
        """Shortcut to quickly add a site manager to the site, and tell it that it belongs to this site."""
        # initialize settings
        self.sitemanager = sitemanager
        # register the site with the site manager
        self.sitemanager.add_site(self)



    def get_package_directory_list(self):
        """Return a list of absolute directory paths where (addon) packages should be scanned"""

        packagedirectories = []
        sitepackages = self.sitesettings.get_sectionvalue(self.DEF_SECTION_config, self.DEF_CONFIGVAR_pkgdirimps_sitempackages)
        if (sitepackages==None):
            pass
        else:
            for sitepackage in sitepackages:
                if (isinstance(sitepackage, basestring)):
                    # it's a string, use it directly
                    packagepath = sitepackage
                else:
                    # it's a module import, get it's directory
                    packagepath = os.path.dirname(os.path.realpath(sitepackage.__file__))
                # add path string to our list
                packagedirectories.append(packagepath)
        #
        return packagedirectories



    def get_sitemodulename(self):
        """Return import of ourself; useful for relative importing."""
        return self.sitemodulename



    def get_pkgdirimp_dotpathprefix_site(self):
        """Return import of ourself; useful for relative importing."""
        from string import join
        modpath = self.sitemodulename
        dirpath = join(modpath.split('.')[:-1],'.')
        return dirpath



    def prepare(self, errors = None):
        """
        Do preparatory stuff after settings have been set.
        It is critical that this function get called prior to running the system.
        """

        if (errors==None):
            errors = EventTracker()
        # misc. stuff
        self.prepare_settings(errors)
        #
        self.discover_packages(errors)
        self.loadinfos_packages(errors)
        self.instantiate_packages(errors)
        #
        self.prepare_routes(errors)
        #
        return errors


    def prepare_settings(self, errors):
        """Prepare some settings."""
        self.controllerroot = self.sitesettings.get_sectionvalue(self.DEF_SECTION_config, self.DEF_CONFIGVAR_controllerroot)

    def prepare_routes(self, errors):
        """Walk all routes and compile/cache/update stuff."""
        self.routes.prepare(self, self, errors)

    def discover_packages(self, errors):
        """Discover packages """
        packagedirectories = self.sitemanager.get_package_directory_list() + self.get_package_directory_list()
        self.packagemanager.set_directories(packagedirectories)
        self.packagemanager.discover_packages()

    def loadinfos_packages(self, errors):
        """Load infos for all packages """
        self.packagemanager.loadinfos_packages()

    def instantiate_packages(self, errors):
        """Load and instantiate packages"""
        self.packagemanager.instantiate_packages()



    def validate(self, errors=None):
        """Validate the site and return an EventTracker with errors and warnings"""
        if (errors==None):
            errors = EventTracker()
        #
        self.validate_setting_config(errors, self.DEF_CONFIGVAR_pkgdirimps_sitempackages, False, "no directory will be scanned for site-specific extensions.")
        self.validate_setting_config(errors, self.DEF_CONFIGVAR_controllerroot, False, "no site-default specified for controller root.")
        self.validate_setting_config(errors, self.DEF_CONFIGVAR_urlprefix, False, "site has no prefix and starts at root (/).")
        #
        return errors


    def validate_setting_config(self, errors, varname, iserror, messagestr):
        """Helper function for the validate() method."""
        if (not self.sitesettings.value_exists(varname, self.DEF_SECTION_config)):
            if (iserror):
                errors.error("Site config variable '"+varname+"' not specified; "+messagestr)
            else:
                errors.warning("Site config variable '"+varname+"' not specified; "+messagestr)



    def setup_early(self):
        """Do early setup stuff.  Most of the functions invoked here are empty and are intended for subclasses to override."""
        self.add_settings_early()
        self.add_loggers()
        self.add_routes()

    def add_settings_early(self):
        """Does nothing in base class, but subclass can overide."""
        pass

    def add_loggers(self):
        """Does nothing in base class, but subclass can overide."""
        pass

    def add_routes(self):
        """Does nothing in base class, but subclass can overide."""
        pass



    def pre_runroute_callable(self, route, request):
        """
        Called after a route is matched, but before it is invoked.
        :return: True to allow route to invoke, or False to prevent it.
        """
        return True


    def post_runroute_callable(self, request):
        """
        Called after a route is invoked.
        :return: False on error
        """
        return True




    def process_request(self, request):
        """
        Run the request through the routes and handle it if it matches any.
        :return: True if the request is for this site and we have set request.response
        """

        ishandled = self.routes.process_request(request, self)
        return ishandled



    def createadd_logger(self,id):
        """Shortcut to create and add and return a logger item."""
        logger = Logger(id)
        self.logmanager.add_logger(logger)
        return logger



    def logerror(self, msg, request, level=Logger.DEF_LEVEL_default, id=Logger.DEF_MESSAGEID_default, extras = {}):
        """Shortcut to add a log message."""
        self.log(msg, Logger.DEF_MTYPE_error, request, level, id, extras)

    def logwarning(self, msg, request, level=Logger.DEF_LEVEL_default, id=Logger.DEF_MESSAGEID_default, extras = {}):
        """Shortcut to add a log message."""
        self.log(msg, Logger.DEF_MTYPE_warning, request, level, id, extras)

    def log(self, msg, mtype, request, level=Logger.DEF_LEVEL_default, id=Logger.DEF_MESSAGEID_default, extras = {}):
        """Shortcut to add a log message by sending it to our log manager."""
        logmessage = MewloLogMessage(msg, request, mtype, level, id, extras)
        self.logmanager.process(logmessage)






    @classmethod
    def create_manager_and_simplesite(cls):
        """This is a convenience (class) helper function to aid in testing of MewloSite derived classes."""
        # create instance of site -- we do it this way so it will create the DERIVED class
        mysite = cls()
        # we need to apply our early settings
        mysite.setup_early()
        # now create a manager using just this site
        sitemanager = mysite.create_and_prepare_standalone_sitemanager()
        # now return the manager
        return sitemanager





    def debug(self,indentstr=""):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = indentstr+"MewloSite (" + self.__class__.__name__ +") reporting in.\n"
        outstr += indentstr+" Site validation:\n"
        outstr += (self.validate()).debug(indentstr+"  ")
        outstr += self.sitesettings.debug(indentstr+" ")
        outstr += self.packagemanager.debug(indentstr+" ")
        outstr += indentstr+" Controller root: "+str(self.get_controllerroot())+"\n"
        outstr += self.routes.debug(indentstr+" ")
        return outstr










class MewloSiteManager(object):
    """
    The MewloManager class holds a collection of Mewlo "sites", which can handle incoming requests.
    Typically, you would have only one single site running from your web server, but there may be times when you want to server multiple sites from a single instantiation running off a single port.
    When supporting multiple sites, the sites are completely independent of one another, and must have completely separate uri prefixes.  They share nothing.
    """

    def __init__(self):
        # the collection of sites that this manager takes care of
        self.sites = list()
        self.prepare_errors = EventTracker()


    def add_site(self,site):
        """Add a site to our list of managed sites."""
        self.sites.append(site)


    def get_installdir(self):
        """Get the directory path of the mewlo installation from the mewlo package."""
        path = os.path.dirname(os.path.realpath(mewlo.__file__))
        return path


    def get_package_directory_list(self):
        """Return a list of directories in the base/install path of Mewlo, where addon packages should be scanned"""
        basedir = self.get_installdir()
        packagedirectories = [basedir+"/"+dir for dir in DefMewlo_BasePackage_subdirlist]
        return packagedirectories


    def prepare(self):
        """Ask all children sites to 'prepare'."""
        for site in self.sites:
            site.prepare(self.prepare_errors)
        return self.prepare_errors


    def debugmessage(self, astr):
        """
        Display a simple debug message with date+time to stdout.
        ATTN: We probably want to remove this later.
        """

        nowtime = datetime.now()
        outstr = "MEWLODEBUG ["+nowtime.strftime("%B %d, %Y at %I:%M%p")+"]: "+astr
        print outstr



    def test_submit_path(self, pathstr):
        """Simulate the submission of a url."""

        outstr = ""
        outstr += "Testing submission of url: "+pathstr+"\n"
        # generate request and debug it
        request = MewloRequest.createrequest_from_pathstring(pathstr)
        outstr += request.debug()
        # generate response and debug it
        self.process_request(request)
        outstr += request.response.debug()
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
            ishandled = site.process_request(request)
            if (ishandled):
                # ok this site handled it
                break

        if (not ishandled):
            # no site handled it, so this is an error
            request.response.add_status_error(404,"Page not found or supported on any site: '"+request.get_path()+"'")

        # return response
        return True



    def wsgiref_callback(self, environ, start_response):
        """Receive a callback from wsgi web server.  We process it and then send response."""

        outstr = "wsgiref_callback:\n"
        outstr += " "+str(environ)+"\n"
        outstr += " "+str(start_response)+"\n"
        self.debugmessage(outstr)
        # create request
        request = MewloRequest.createrequest_from_wsgiref_environ(environ)
        # get response
        ishandled = self.process_request(request)
        # process response
        return request.response.start_and_make_wsgiref_response(start_response)



    def preprocess_request(self, request):
        """Pre-process and parse the request.  Here we might add stuff to it before asking child sites to look at it."""
        request.preprocess()





    def debug(self,indentstr=''):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = indentstr+"MewloSiteManager reporting in.\n"
        outstr += self.prepare_errors.debug(indentstr+" ")
        outstr += self.debug_sites(indentstr+" ")
        return outstr

    def debug_sites(self,indentstr=" "):
        """Debug helper; return string with recursive debug info from child sites."""
        outstr = indentstr+"Sites:\n"
        indentstr+=" "
        if (len(self.sites)==0):
            outstr += indentstr+"None.\n"
        for site in self.sites:
            outstr += site.debug(indentstr+" ")+"\n"
        return outstr


