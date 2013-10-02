"""
msite.py
This file contains classes to handle Mewlo site class.
"""


# mewlo imports
from mpackage import MewloPackageManager
from mrequest import MewloRequest
from mresponse import MewloResponse
from mroutemanager import MewloRouteGroup
from mglobals import mewlosite, set_mewlosite, debugmode


# helper imports
from helpers.event.event import Event, EventList, EWarning, EError, EDebug
from helpers.event.logger import LogManager, Logger
from helpers.settings import Settings
from helpers.event.logger_filetarget import LogTarget_File
from helpers.misc import get_value_from_dict

from msignals import MewloSignalDispatcher
from mregistry import MewloComponentRegistry
from helpers.misc import resolve_expand_string


# python imports
import os
from datetime import datetime, date, time











class MewloSite(object):
    """
    The MewloSite class represents a single "site" that handles requests.
    Typically you will only have one site running.
    """

    # class constants
    # setting sections
    DEF_SECTION_config = 'config'
    DEF_SECTION_aliases = 'aliases'
    DEF_SECTION_packages = 'packages'
    # settings
    DEF_SETTINGNAME_pkgdirimps_sitempackages = 'pkgdirimps_sitempackages'
    DEF_SETTINGNAME_controllerroot = 'controllerroot'
    DEF_SETTINGNAME_siteurl_internal = 'siteurl_internal'
    DEF_SETTINGNAME_siteurl_absolute = 'siteurl_absolute'
    DEF_SETTINGNAME_sitefilepath = 'sitefilepath'
    DEF_SETTINGNAME_default_logfilename = 'logfilename'
    DEF_SETTINGNAME_logfilepath = 'logfilepath'
    # default values
    DEF_SETTINGVAL_default_logfilename_defaultvalue = '${logfilepath}/mewlo.log'
    DEF_SETTINGVAL_default_package_settings = { 'enabled': False }
    #
    DEF_Mewlo_BasePackage_subdirlist = ['mpackages']
    # so others can interogate state of site and tell when it is shutting down, etc
    DEF_SITESTATE_INITIALIZE_START = 'initializing'
    DEF_SITESTATE_INITIALIZE_END = 'initialized'
    DEF_SITESTATE_STARTUP_START = 'starting'
    DEF_SITESTATE_STARTUP_END = 'started'
    DEF_SITESTATE_SHUTDOWN_START = 'shuttingdown'
    DEF_SITESTATE_SHUTDOWN_END = 'shutdown'

    def __init__(self, sitemodulename):
        # Nothing that could fail should be done in this __init__ -- save that for later functions
        # initialize settings
        self.fallbacklogger = None

        # setup log manager -- let's do this first so that log manager can receive messages
        self.logmanager = LogManager()

        # set site name
        self.sitename = self.__class__.__name__

        # set global variable
        set_mewlosite(self)

        # now update site state
        self.set_state(MewloSite.DEF_SITESTATE_INITIALIZE_START)

        # init other stuff
        self.sitemanager = None
        self.controllerroot = None
        #
        # create site settings
        self.settings = Settings()
        # collection of mewlo addon packages
        self.packagemanager = MewloPackageManager()
        # route manager
        self.routes = MewloRouteGroup()
        # signal dispatcher
        self.dispatcher = MewloSignalDispatcher()
        # component registry
        self.registry = MewloComponentRegistry()
        #
        # record package of the site for relative imports
        self.sitemodulename = sitemodulename
        #
        # update state
        self.set_state(MewloSite.DEF_SITESTATE_INITIALIZE_END)







    def debuglog(self, msg, request = None):
        """
        Shortcut to log a debug message.
        ATTN: TODO - rewrite this.
        """
        self.logevent(msg, request)


    def logevent(self, mevent, request = None):
        """Shortcut to add a log message from an event/failure."""
        # convert it to an event if its just a plain string
        if (isinstance(mevent, basestring)):
            mevent = EDebug(mevent)
        # add request field (if it wasn't already set in mevent)
        if (request != None):
            missingfields = { 'request': self }
            mevent.mergemissings(missingfields)
        # log it
        self.logmanager.process(mevent)


    def logevents(self, mevents, request = None):
        """Shortcut to add a log message from a *possible* iterable of events."""
        for mevent in mevents:
            self.logevent(mevent, request)





    def set_state(self, stateval):
        # print "ATTN: DEBUG SITE IS ENTERING STATE: "+stateval
        self.state = stateval
        if (debugmode()):
            self.debuglog("Site changes to state '{0}'.".format(stateval))


    def set_sitemanager(self, sitemanager):
        """Set sitemanager reference."""
        self.sitemanager = sitemanager






    def get_controllerroot(self):
        return self.controllerroot
    def get_sitename(self):
        return self.sitename
    def get_id(self):
        # generic get_id function used in lots of places to help display debug info
        return self.get_sitename()


    def get_installdir(self):
        """Get the directory path of the mewlo installation from the mewlo package."""
        import mewlo
        path = os.path.dirname(os.path.realpath(mewlo.__file__))
        return path


    def get_root_package_directory_list(self):
        """Return a list of directories in the base/install path of Mewlo, where addon packages should be scanned"""
        basedir = self.get_installdir()
        packagedirectories = [basedir + '/' + dir for dir in MewloSite.DEF_Mewlo_BasePackage_subdirlist]
        return packagedirectories



    def merge_settings(self, settings):
        """Merge in some settings to our site settings."""
        self.settings.merge_settings(settings)





    def get_site_package_directory_list(self):
        """Return a list of absolute directory paths where (addon) packages should be scanned"""

        packagedirectories = []
        sitepackages = self.settings.get_sectionvalue(MewloSite.DEF_SECTION_config, MewloSite.DEF_SETTINGNAME_pkgdirimps_sitempackages)
        if (sitepackages == None):
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
        dirpath = join(modpath.split('.')[:-1], '.')
        return dirpath






    def startup(self, eventlist = None):
        """
        Do preparatory stuff after settings have been set.
        It is critical that this function get called prior to running the system.
        """

        # update state
        self.set_state(MewloSite.DEF_SITESTATE_STARTUP_START)

        # we log errors/warnings to an eventlist and return it; either one we are passed or we create a new one if needed
        if (eventlist == None):
            eventlist = EventList()


        # any settings caching or other pre-preparation we need to do
        self.preprocess_settings(eventlist)

        # validate site and settings first to make sure all is good
        self.validate(eventlist)


        # startup our helpers
        #
        # log system
        self.logmanager.startup(eventlist)
        # dispatcher
        self.dispatcher.startup(eventlist)
        # registry
        self.registry.startup(eventlist)
        # packages (will load and instantiate enabled packages)
        self.packagemanager.startup(eventlist)
        # routes
        self.routes.startup(self, eventlist)


        # log all startup events
        self.logevents(eventlist)

        # update state
        self.set_state(MewloSite.DEF_SITESTATE_STARTUP_END)
        #
        return eventlist






    def shutdown(self, eventlist = None):
        """Shutdown everything."""
        # update state
        self.set_state(MewloSite.DEF_SITESTATE_SHUTDOWN_START)
        # shutdown routes
        self.routes.shutdown()
        # shutdown packages
        self.packagemanager.shutdown()
        # startup dispatcher
        self.dispatcher.shutdown()
        # startup registry
        self.registry.shutdown()
        # update state
        self.set_state(MewloSite.DEF_SITESTATE_SHUTDOWN_END)
        # shutdown log system
        self.logmanager.shutdown()
        # done
        return eventlist

















    def preprocess_settings(self, eventlist):
        """We may want to preprocess/cache some settings before we start."""
        # cache some stuff?
        self.controllerroot = self.settings.get_sectionvalue(MewloSite.DEF_SECTION_config, MewloSite.DEF_SETTINGNAME_controllerroot)
        # package manager init
        self.packagemanager.set_directories( self.get_root_package_directory_list() + self.get_site_package_directory_list() )
        self.packagemanager.set_packagesettings( self.settings.get_value(MewloSite.DEF_SECTION_packages) )
        self.packagemanager.set_default_packagesettings(MewloSite.DEF_SETTINGVAL_default_package_settings)







    def validate(self, eventlist=None):
        """Validate settings and return an EventList with errors and warnings"""
        if (eventlist == None):
            eventlist = EventList()
        #
        self.validate_setting_config(eventlist, MewloSite.DEF_SETTINGNAME_pkgdirimps_sitempackages, False, "no directory will be scanned for site-specific extensions.")
        self.validate_setting_config(eventlist, MewloSite.DEF_SETTINGNAME_controllerroot, False, "no site-default specified for controller root.")
        # required stuff
        self.validate_setting_config(eventlist, MewloSite.DEF_SETTINGNAME_siteurl_internal, True, "site has no relative url specified; assumed to start at root (/).")
        self.validate_setting_config(eventlist, MewloSite.DEF_SETTINGNAME_siteurl_absolute, True, "site has no absolute url address.")
        self.validate_setting_config(eventlist, MewloSite.DEF_SETTINGNAME_sitefilepath, True, "site has no filepath specified for it's home directory.")

        # return events encountered
        return eventlist




    def validate_setting_config(self, eventlist, varname, iserror, messagestr):
        """Helper function for the validate() method."""
        if (not self.settings.value_exists(varname, MewloSite.DEF_SECTION_config)):
            estr = "In site '{0}', site config variable '{1}' not specified; {2}".format(self.get_sitename(),varname,messagestr)
            if (iserror):
                eventlist.add(EError(estr))
            else:
                eventlist.add(EWarning(estr))



    def setup_early(self):
        """Do early setup stuff.  Most of the functions invoked here are empty and are intended for subclasses to override."""
        self.add_settings_early()
        self.add_default_settings()
        self.add_loggers()
        self.add_routes()
        # we add fallback loggers at END, after user-site added loggers
        self.add_fallback_loggers()

    def add_settings_early(self):
        """Does nothing in base class, but subclass can overide."""
        pass

    def add_loggers(self):
        """Does nothing in base class, but subclass can overide."""
        pass

    def add_routes(self):
        """Does nothing in base class, but subclass can overide."""
        pass



    def add_default_settings(self):
        """Set some default overrideable settings."""
        self.set_default_settings_config()
        self.set_default_settings_aliases()


    def set_default_settings_config(self):
        """Set default config settings."""
        config = {
            MewloSite.DEF_SETTINGNAME_default_logfilename: MewloSite.DEF_SETTINGVAL_default_logfilename_defaultvalue,
            }
        self.settings.merge_settings_atsection(MewloSite.DEF_SECTION_config, config)


    def set_default_settings_aliases(self):
        """Set default alias settings."""
        aliases = {
            MewloSite.DEF_SETTINGNAME_siteurl_absolute: self.settings.get_sectionvalue(MewloSite.DEF_SECTION_config, MewloSite.DEF_SETTINGNAME_siteurl_absolute),
            MewloSite.DEF_SETTINGNAME_siteurl_internal: self.settings.get_sectionvalue(MewloSite.DEF_SECTION_config, MewloSite.DEF_SETTINGNAME_siteurl_internal),
            MewloSite.DEF_SETTINGNAME_sitefilepath: self.settings.get_sectionvalue(MewloSite.DEF_SECTION_config, MewloSite.DEF_SETTINGNAME_sitefilepath),
            MewloSite.DEF_SETTINGNAME_logfilepath: '${sitefilepath}/logging',
            }
        self.settings.merge_settings_atsection(MewloSite.DEF_SECTION_aliases, aliases)




    def add_fallback_loggers(self):
        """Create any default fallback loggers that we should always put in place."""
        # We create a fallback default file logger that will log everything from current run to file, and reset each run
        # ATTN:TODO - we will want to later change this to logrotate or something

        # create a single logger (with no filters); multiple loggers are supported because each logger can have filters that define what this logger filters out
        self.fallbacklogger = self.add_logger(Logger('FallbackLogger'))

        # now add some targets (handlers) to it
        fpath = self.settings.get_sectionvalue(MewloSite.DEF_SECTION_config, MewloSite.DEF_SETTINGNAME_default_logfilename)
        self.fallbacklogger.add_target(LogTarget_File(filename=self.resolvealias(fpath), filemode='w'))




















    def pre_runroute_callable(self, route, request):
        """
        Called after a route is matched, but before it is invoked.
        :return: failure on error
        """
        return None


    def post_runroute_callable(self, request):
        """
        Called after a route is invoked.
        :return: failure on error
        """
        return None




    def process_request(self, request):
        """
        Run the request through the routes and handle it if it matches any.
        :return: True if the request is for this site and we have set request.response
        """

        ishandled = self.routes.process_request(request)
        return ishandled



    def add_logger(self, logger):
        """Just ask the logmanager to add the logger."""
        self.logmanager.add_logger(logger)
        return logger






    @classmethod
    def create_manager_and_instantiate_site(cls):
        """
        This is a convenience (class) helper function to aid in testing of MewloSite derived classes.
        So the following two lines of code are equivelent:
            sitemanager = MewloSiteManager(MewloSite_Test1)
            sitemanager = MewloSite_Test1.create_manager_and_instantiate_site()
        I find the former more readable; the only advantage of the latter is that it does not require us to import MewloSitemanager.
        """
        # create site manager and ask it to instantiate and take ownership of the site defined by the class
        sitemanager = MewloSiteManager(cls)
        # now return the manager
        return sitemanager






    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = " "*indent + "MewloSite (" + self.__class__.__name__ + ") reporting in.\n"
        indent += 1
        outstr += " "*indent + "Site validation:\n"
        outstr += (self.validate()).dumps(indent+1)
        outstr += "\n"
        outstr += self.settings.dumps(indent+1)
        outstr += "\n"
        outstr += self.dispatcher.dumps(indent+1)
        outstr += "\n"
        outstr += self.registry.dumps(indent+1)
        outstr += "\n"
        outstr += self.packagemanager.dumps(indent+1)
        outstr += " "*indent+"Routes:\n"
        outstr += self.routes.dumps(indent+1)
        return outstr



    def resolvealias(self, alias):
        """Resolve an alias."""
        resolvedstr = resolve_expand_string(alias, self.settings.get_value(MewloSite.DEF_SECTION_aliases))
        return resolvedstr


    def absolute_filepath(self, relpath):
        """Shortcut to resolve a filepath given a relative path."""
        return self.resolvealias('${sitefilepath}' + relpath)

    def absolute_url(self, relpath):
        """Shortcut to resolve a url given a relative path."""
        return self.resolvealias('${siteurl_absolute}' + relpath)

    def internal_url(self, relpath):
        """Shortcut to resolve a url given a relative path."""
        return self.resolvealias('${siteurl_internal}' + relpath)







class MewloSiteManager(object):
    """
    The MewloManager class holds a collection of Mewlo "sites", which can handle incoming requests.
    Typically, you would have only one single site running from your web server, but there may be times when you want to server multiple sites from a single instantiation running off a single port.
    When supporting multiple sites, the sites are completely independent of one another, and must have completely separate uri prefixes.  They share nothing.
    """


    def __init__(self, siteclass=None):
        # the collection of sites that this manager takes care of
        self.sites = list()
        self.prepeventlist = EventList()
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
        site = siteclass()
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
        request = MewloRequest.createrequest_from_pathstring(pathstr)
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
            set_mewlosite(site)
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
        request = MewloRequest.createrequest_from_wsgiref_environ(environ)
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


