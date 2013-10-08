"""
msite.py
This file contains classes to handle Mewlo site class.
"""


# mewlo imports
import mpackage
import mroute
import mglobals
import msitemanager
import msignal
import mregistry
import mdbmanager


# helper imports
from helpers.event.event import Event, EventList, EWarning, EError, EDebug
from helpers.event.logger import LogManager, Logger
from helpers.settings.settings import Settings
from helpers.settings.dbsettings import DbSettings
from helpers.event.logger_filetarget import LogTarget_File
from helpers.misc import get_value_from_dict
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
    DEF_SECTION_database = 'database'
    # settings
    DEF_SETTINGNAME_pkgdirimps_sitempackages = 'pkgdirimps_sitempackages'
    DEF_SETTINGNAME_controllerroot = 'controllerroot'
    DEF_SETTINGNAME_siteurl_internal = 'siteurl_internal'
    DEF_SETTINGNAME_siteurl_absolute = 'siteurl_absolute'
    DEF_SETTINGNAME_sitefilepath = 'sitefilepath'
    DEF_SETTINGNAME_default_logfilename = 'logfilename'
    DEF_SETTINGNAME_logfilepath = 'logfilepath'
    DEF_SETTINGNAME_dbfilepath = 'dbfilepath'
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

    def __init__(self, sitemodulename, debugmode):
        # Nothing that could fail should be done in this __init__ -- save that for later functions
        # initialize settings
        self.fallbacklogger = None

        # default debugmode
        self.debugmode = debugmode

        # setup log manager -- let's do this first so that log manager can receive messages
        self.logmanager = LogManager(self.debugmode)

        # set site name
        self.sitename = self.__class__.__name__

        # set global variable
        mglobals.set_mewlosite(self)

        # now update site state
        self.set_state(MewloSite.DEF_SITESTATE_INITIALIZE_START)

        # init other stuff
        self.sitemanager = None
        self.controllerroot = None
        #
        # create (non-db-persistent) site settings -- these are set by configuration at runtime
        self.settings = Settings()
        #
        # database manager
        self.dbmanager = mdbmanager.MewloDatabaseManager()
        #
        # create persistent(db) package settings
        self.packagesettings = DbSettings()
        #
        # collection of mewlo addon packages
        self.packagemanager = mpackage.MewloPackageManager()
        # route manager
        self.routes = mroute.MewloRouteGroup()
        # signal dispatcher
        self.dispatcher = msignal.MewloSignalDispatcher()
        # component registry
        self.registry = mregistry.MewloComponentRegistry()
        #
        # record package of the site for relative imports
        self.sitemodulename = sitemodulename
        #
        # update state
        self.set_state(MewloSite.DEF_SITESTATE_INITIALIZE_END)


    def set_debugmode(self, val):
        """Set debugmode for the site, which may also have to pass on this value to components."""
        #ATTN:TODO - right now we are using a global
        self.debugmode = val
        self.logmanager.set_debugmode(val)

    def get_debugmode(self):
        """Return the debubmode."""
        return self.debugmode


    def get_packagesettings(self):
        return self.packagesettings


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
        if (mglobals.debugmode()):
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
        sitepackages = self.settings.get_subvalue(MewloSite.DEF_SECTION_config, MewloSite.DEF_SETTINGNAME_pkgdirimps_sitempackages)
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

        # first are main settings -- this startup usually does nothing since these settings are not persistent
        self.settings.startup(eventlist)

        # any settings caching or other pre-preparation we need to do
        self.preprocess_settings(eventlist)

        # validate site and settings first to make sure all is good
        self.validate(eventlist)


        # startup our helpers
        #
        # database manager
        self.dbmanager.startup(eventlist)
        # package settings -- these are persistent and let packages (extensions/plugins) store persistent settings
        self.packagesettings.startup(eventlist)
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
        #print "*** IN SITE SHUTDOWN ***"
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
        # database manager
        self.dbmanager.shutdown()
        # update state
        self.set_state(MewloSite.DEF_SITESTATE_SHUTDOWN_END)
        # shutdown log system
        self.logmanager.shutdown()
        # done
        return eventlist

















    def preprocess_settings(self, eventlist):
        """We may want to preprocess/cache some settings before we start."""
        # cache some stuff?
        self.controllerroot = self.settings.get_subvalue(MewloSite.DEF_SECTION_config, MewloSite.DEF_SETTINGNAME_controllerroot)
        # package manager init
        self.packagemanager.set_directories( self.get_root_package_directory_list() + self.get_site_package_directory_list() )
        self.packagemanager.set_packagesettings( self.settings.get_value(MewloSite.DEF_SECTION_packages) )
        self.packagemanager.set_default_packagesettings(MewloSite.DEF_SETTINGVAL_default_package_settings)
        # database manager init
        self.dbmanager.set_databasesettings( self.settings.get_value(MewloSite.DEF_SECTION_database) )



























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
        if (not self.settings.value_exists(MewloSite.DEF_SECTION_config, varname)):
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
        self.settings.merge_settings_property(MewloSite.DEF_SECTION_config, config)


    def set_default_settings_aliases(self):
        """Set default alias settings."""
        aliases = {
            MewloSite.DEF_SETTINGNAME_siteurl_absolute: self.settings.get_subvalue(MewloSite.DEF_SECTION_config, MewloSite.DEF_SETTINGNAME_siteurl_absolute),
            MewloSite.DEF_SETTINGNAME_siteurl_internal: self.settings.get_subvalue(MewloSite.DEF_SECTION_config, MewloSite.DEF_SETTINGNAME_siteurl_internal),
            MewloSite.DEF_SETTINGNAME_sitefilepath: self.settings.get_subvalue(MewloSite.DEF_SECTION_config, MewloSite.DEF_SETTINGNAME_sitefilepath),
            MewloSite.DEF_SETTINGNAME_logfilepath: '${sitefilepath}/logging',
            MewloSite.DEF_SETTINGNAME_dbfilepath: '${sitefilepath}/database',
            }
        self.settings.merge_settings_property(MewloSite.DEF_SECTION_aliases, aliases)




    def add_fallback_loggers(self):
        """Create any default fallback loggers that we should always put in place."""
        # We create a fallback default file logger that will log everything from current run to file, and reset each run
        # ATTN:TODO - we will want to later change this to logrotate or something

        # create a single logger (with no filters); multiple loggers are supported because each logger can have filters that define what this logger filters out
        self.fallbacklogger = self.add_logger(Logger('FallbackLogger'))

        # now add some targets (handlers) to it
        fpath = self.settings.get_subvalue(MewloSite.DEF_SECTION_config, MewloSite.DEF_SETTINGNAME_default_logfilename)
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
        sitemanager = msitemanager.MewloSiteManager(cls)
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
        outstr += self.dbmanager.dumps(indent+1)
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
