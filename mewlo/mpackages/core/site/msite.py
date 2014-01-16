"""
msite.py
This file contains classes to handle Mewlo site class.
"""


# mewlo imports
import msitemanager
from .. import mglobals
from ..package import mpackagemanager
from ..route import mroute
from ..signal import msignal
from ..registry import mregistry
from ..setting.msettings import MewloSettings
from ..database import mdbsettings
from ..database import mdbmanager_sqlalchemy
from ..database import mdbmodel_settings
from ..database import mdbmodel_gob
from ..rbac import mrbac
from ..navnode import mnav
from ..template import mtemplate
from ..template import mtemplatehelper
from ..asset import massetmanager
from ..eventlog import mlogger
from ..eventlog.mevent import Event, EventList, EWarning, EError, EDebug
from ..eventlog.mlogger import MewloLogger
from ..eventlog.mlogtarget_file import MewloLogTarget_File
from ..helpers.misc import get_value_from_dict
from ..helpers.misc import resolve_expand_string
from ..user import muser
from ..group import mgroup
from ..rbac import mrbac

# python imports
import os
from datetime import datetime, date, time











class MewloSite(object):
    """
    The MewloSite class represents a single "site" that handles requests.
    Typically you will only have one site running.
    """



    def __init__(self, sitemodulename, debugmode):
        # Nothing that could fail should be done in this __init__ -- save that for later functions

        # set global variable
        mglobals.set_mewlosite(self)

        # default debugmode
        self.debugmode = debugmode
        # set site name
        self.sitename = self.__class__.__name__
        # record package of the site for relative imports
        self.sitemodulename = sitemodulename
        # init misc. settings
        self.sitemanager = None
        self.controllerroot = None
        self.fallbacklogger = None
        # exposed to templates
        self.templatehelper = None


        # setup log manager helper early so that log manager can receive messages
        self.logmanager = mlogger.MewloLogManager(self.debugmode)

        # now update site state
        self.set_state(MewloSettings.DEF_SITESTATE_INITIALIZE_START)

        # create helpers

        # create (non-db-persistent) site settings -- these are set by configuration at runtime
        self.settings = MewloSettings()

        # database manager
        self.dbmanager = mdbmanager_sqlalchemy.MewloDatabaseManagerSqlA()

        # rbac permission manager
        self.rbac = mrbac.MewloRbacManager()

        # create persistent(db) package settings
        self.packagesettings = mdbsettings.MewloSettingsDb(MewloSettings.DEF_DBCLASSNAME_PackageSettings)

        # collection of mewlo addon packages
        self.packagemanager = mpackagemanager.MewloPackageManager()

        # route manager
        self.routemanager = mroute.MewloRouteManager()

        # signal dispatcher
        self.dispatcher = msignal.MewloSignalManager()

        # component registry
        self.registry = mregistry.MewloRegistryManager()

        # navnode manager
        self.navnodes = mnav.NavNodeManager()

        # template manager
        self.templates = mtemplate.MewloTemplateManager()

        # assetmanager
        self.assetmanager = massetmanager.MewloAssetManager()

        # template helper
        self.templatehelper = mtemplatehelper.MewloTemplateHelper()

        # update state
        self.set_state(MewloSettings.DEF_SITESTATE_INITIALIZE_END)









    def startup(self, eventlist = None):
        """
        Do preparatory stuff after settings have been set.
        It is critical that this function get called prior to running the system.
        """

        # update state
        self.set_state(MewloSettings.DEF_SITESTATE_STARTUP_START)

        # we log errors/warnings to an eventlist and return it; either one we are passed or we create a new one if needed
        if (eventlist == None):
            eventlist = EventList()

        # first are main settings -- this startup usually does nothing since these settings are not persistent
        self.settings.startup(self, eventlist)

        # asset manager
        self.assetmanager.startup(self, eventlist)

        # any settings caching or other pre-preparation we need to do
        self.preprocess_settings(eventlist)

        # validate site and settings first to make sure all is good
        self.validate(eventlist)


        # startup our helpers

        # registry
        self.registry.startup(self, eventlist)


        # database manager
        self.dbmanager.startup(self, eventlist)
        # we need to create some classes very early so that plugins can access them
        self.create_early_database_classes(eventlist)
        # and to create the tables for them, etc.
        self.dbmanager.create_tableandmapper_forallmodelclasses()

        # rbac system
        self.rbac.startup(self, eventlist)

        # log system
        self.logmanager.startup(self, eventlist)

        # dispatcher
        self.dispatcher.startup(self, eventlist)

        # routes
        self.routemanager.startup(self, eventlist)

        # nav nodes
        self.navnodes.startup(self, eventlist)

        # package settings -- these are persistent and let packages (extensions/plugins) store persistent settings
        self.packagesettings.startup(self, eventlist)

        # packages (will load and instantiate enabled packages)
        self.packagemanager.startup(self, eventlist)

        # Now we are ready to create the rest of the core database classes
        self.create_core_database_classes(eventlist)
        # and to create the tables for them, etc.
        self.dbmanager.create_tableandmapper_forallmodelclasses()

        # templater
        self.templates.startup(self, eventlist)

        # template helper
        self.templatehelper.startup(self, eventlist)

        # log all startup events
        self.logevents(eventlist)

        # update state
        self.set_state(MewloSettings.DEF_SITESTATE_STARTUP_END)
        #
        return eventlist








    def shutdown(self, eventlist = None):
        """Shutdown everything."""

        # update state
        self.set_state(MewloSettings.DEF_SITESTATE_SHUTDOWN_START)

        # asset manager
        self.assetmanager.shutdown()

        # templates
        self.templates.shutdown()

        # packages
        self.packagemanager.shutdown()

        # package settings
        self.packagesettings.shutdown()

        # routes
        self.routemanager.shutdown()

        # dispatcher
        self.dispatcher.shutdown()

        # navnode manager
        self.navnodes.shutdown()

        # registry
        self.registry.shutdown()

        # template helper
        self.templatehelper.shutdown()

        # rbac system
        self.rbac.shutdown()

        #  log system
        self.logmanager.shutdown()

        # database manager
        self.dbmanager.shutdown()

        # update state (note this won't be logged since we will have shutdown log/db by now)
        self.set_state(MewloSettings.DEF_SITESTATE_SHUTDOWN_END)

        # done
        return eventlist
























    def ensure_earlydatabasemodels_mapped(self):
        """Some database models must be defined in early startup."""
        #modelclasslist = []
        #self.dbmanager.earlycreate_formodelclasslist(modelclasslist)
        pass












    def preprocess_settings(self, eventlist):
        """We may want to preprocess/cache some settings before we start."""
        # cache some stuff?
        self.controllerroot = self.settings.get_subvalue(MewloSettings.DEF_SECTION_config, MewloSettings.DEF_SETTINGNAME_controllerroot)
        # package manager init
        self.packagemanager.set_directories( self.get_root_package_directory_list() + self.get_site_package_directory_list() )
        self.packagemanager.set_packagesettings( self.settings.get_value(MewloSettings.DEF_SECTION_packages) )
        self.packagemanager.set_default_packagesettings(MewloSettings.DEF_SETTINGVAL_default_package_settings)
        # database manager init
        self.dbmanager.set_databasesettings( self.settings.get_value(MewloSettings.DEF_SECTION_database) )







    def validate(self, eventlist=None):
        """Validate settings and return an EventList with errors and warnings"""
        if (eventlist == None):
            eventlist = EventList()
        #
        self.validate_setting_config(eventlist, MewloSettings.DEF_SETTINGNAME_pkgdirimps_sitempackages, False, "no directory will be scanned for site-specific extensions.")
        self.validate_setting_config(eventlist, MewloSettings.DEF_SETTINGNAME_controllerroot, False, "no site-default specified for controller root.")
        # required stuff
        self.validate_setting_config(eventlist, MewloSettings.DEF_SETTINGNAME_siteurl_relative, True, "site has no relative url specified; assumed to start at root (/).")
        self.validate_setting_config(eventlist, MewloSettings.DEF_SETTINGNAME_siteurl_absolute, True, "site has no absolute url address.")
        self.validate_setting_config(eventlist, MewloSettings.DEF_SETTINGNAME_sitefilepath, True, "site has no filepath specified for it's home directory.")

        # return events encountered
        return eventlist


    def validate_setting_config(self, eventlist, varname, iserror, messagestr):
        """Helper function for the validate() method."""
        if (not self.settings.value_exists(MewloSettings.DEF_SECTION_config, varname)):
            estr = "In site '{0}', site config variable '{1}' not specified; {2}".format(self.get_sitename(),varname,messagestr)
            if (iserror):
                eventlist.add(EError(estr))
            else:
                eventlist.add(EWarning(estr))




























    def logevent(self, event, request = None):
        """Shortcut to add a log message from an event/failure."""
        # convert it to an event if its just a plain string
        if (isinstance(event, basestring)):
            event = EDebug(event)
        # add request field (if it wasn't already set in mevent)
        if (request != None):
            missingfields = { 'request': request }
            event.mergemissings(missingfields)
        # log it
        self.logmanager.process(event)


    def logevents(self, events, request = None):
        """Shortcut to add a log message from a *possible* iterable of events."""
        for event in events:
            self.logevent(event, request)










    def set_debugmode(self, val):
        """Set debugmode for the site, which may also have to pass on this value to components."""
        self.debugmode = val
        self.logmanager.set_debugmode(val)

    def get_debugmode(self):
        """Return the debubmode."""
        return self.debugmode



    def set_state(self, stateval):
        self.state = stateval
        if (self.get_debugmode()):
            self.logevent("Site changes to state '{0}'.".format(stateval))

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


    def get_sitemodulename(self):
        """Return import of ourself; useful for relative importing."""
        return self.sitemodulename


    def get_installdir(self):
        """Get the directory path of the mewlo installation from the mewlo package."""
        import mewlo
        path = os.path.dirname(os.path.realpath(mewlo.__file__))
        return path


    def get_root_package_directory_list(self):
        """Return a list of directories in the base/install path of Mewlo, where addon packages should be scanned"""
        basedir = self.get_installdir()
        packagedirectories = [basedir + '/' + dir for dir in MewloSettings.DEF_Mewlo_BasePackage_subdirlist]
        return packagedirectories


    def get_site_package_directory_list(self):
        """Return a list of absolute directory paths where (addon) packages should be scanned"""

        packagedirectories = []
        sitepackages = self.settings.get_subvalue(MewloSettings.DEF_SECTION_config, MewloSettings.DEF_SETTINGNAME_pkgdirimps_sitempackages)
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


    def get_pkgdirimp_dotpathprefix_site(self):
        """Return import of ourself; useful for relative importing."""
        from string import join
        modpath = self.sitemodulename
        dirpath = join(modpath.split('.')[:-1], '.')
        return dirpath






























    def setup_early(self):
        """Do early setup stuff.  Most of the functions invoked here are empty and are intended for subclasses to override."""
        self.add_settings_early()
        self.add_default_settings()
        self.add_loggers()
        self.add_routes()
        self.add_navnodes()
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

    def add_navnodes(self):
        """Does nothing in base class, but subclass can overide."""
        pass










    def merge_settings(self, settings):
        """Merge in some settings to our site settings."""
        self.settings.merge_settings(settings)


    def add_default_settings(self):
        """Set some default overrideable settings."""
        self.set_default_settings_config()
        self.set_default_settings_aliases()


    def set_default_settings_config(self):
        """Set default config settings."""
        config = {
            MewloSettings.DEF_SETTINGNAME_default_logfilename: MewloSettings.DEF_SETTINGVAL_default_logfilename_defaultvalue,
            }
        self.settings.merge_settings_key(MewloSettings.DEF_SECTION_config, config)


    def set_default_settings_aliases(self):
        """Set default alias settings."""
        aliases = {
            MewloSettings.DEF_SETTINGNAME_siteurl_absolute: self.settings.get_subvalue(MewloSettings.DEF_SECTION_config, MewloSettings.DEF_SETTINGNAME_siteurl_absolute),
            MewloSettings.DEF_SETTINGNAME_siteurl_relative: self.settings.get_subvalue(MewloSettings.DEF_SECTION_config, MewloSettings.DEF_SETTINGNAME_siteurl_relative),
            MewloSettings.DEF_SETTINGNAME_sitefilepath: self.settings.get_subvalue(MewloSettings.DEF_SECTION_config, MewloSettings.DEF_SETTINGNAME_sitefilepath),
            MewloSettings.DEF_SETTINGNAME_logfilepath: '${sitefilepath}/logging',
            MewloSettings.DEF_SETTINGNAME_dbfilepath: '${sitefilepath}/database',
            MewloSettings.DEF_SETTINGNAME_siteview_filepath: '${sitefilepath}/views',
            MewloSettings.DEF_SETTINGNAME_sitename: self.settings.get_subvalue(MewloSettings.DEF_SECTION_config, MewloSettings.DEF_SETTINGNAME_sitename),

            }
        self.settings.merge_settings_key(MewloSettings.DEF_SECTION_aliases, aliases)
        self.alias_settings_change()



    def alias_settings_change(self):
        """Inform asset manager of new alias settings.  This *must* be called whenever alias settings may change."""
        self.assetmanager.set_alias_settings(self.settings.get_value(MewloSettings.DEF_SECTION_aliases))








    def add_logger(self, logger):
        """Just ask the logmanager to add the logger."""
        self.logmanager.add_logger(logger)
        return logger


    def add_fallback_loggers(self):
        """Create any default fallback loggers that we should always put in place."""
        # We create a fallback default file logger that will log everything from current run to file, and reset each run
        # ATTN:TODO - we will want to later change this to logrotate or something

        # create a single logger (with no filters); multiple loggers are supported because each logger can have filters that define what this logger filters out
        self.fallbacklogger = self.add_logger(MewloLogger('FallbackLogger'))

        # now add some targets (handlers) to it
        fpath = self.settings.get_subvalue(MewloSettings.DEF_SECTION_config, MewloSettings.DEF_SETTINGNAME_default_logfilename)
        self.fallbacklogger.add_target(MewloLogTarget_File(filename=self.resolve(fpath), filemode='w'))



    def create_early_database_classes(self, eventlist):
        """Setup some database classes.
        ATTN: We may want to move this elsewhere eventually.
        """
        # create some really early database model classes that must exist prior to other early stuff
        # NOTE: we call create_derived_dbmodelclass() to dynamically on the fly create a new model class based on an existing one, but with unique table, etc.
        dbmanager = self.dbmanager
        newclass = dbmanager.create_derived_dbmodelclass(self, mdbmodel_settings.MewloDbModel_Settings, MewloSettings.DEF_DBCLASSNAME_PackageSettings, MewloSettings.DEF_DBTABLENAME_PackageSettings)
        dbmanager.register_modelclass(self, newclass)
        newclass = self.dbmanager.create_derived_dbmodelclass(self, mdbmodel_settings.MewloDbModel_Settings, MewloSettings.DEF_DBCLASSNAME_MainSettings, MewloSettings.DEF_DBTABLENAME_MainSettings)
        dbmanager.register_modelclass(self, newclass)
        #
        dbmanager.register_modelclass(self, mdbmodel_gob.MewloDbModel_Gob)




    def create_core_database_classes(self, eventlist):
        """Setup some database classes.
        ATTN: We may want to move this elsewhere eventually.
        """
        # create some core database model classes
        dbmanager = self.dbmanager
        # ATTN: Again, we should do this elsewhere
        dbmanager.register_modelclass(self, muser.MewloUser)
        dbmanager.register_modelclass(self, mgroup.MewloGroup)
        dbmanager.register_modelclass(self, mrbac.MewloRole)
        dbmanager.register_modelclass(self, mrbac.MewloRoleHierarchy)
        dbmanager.register_modelclass(self, mrbac.MewloRoleAssignment)











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
        # before we start a request we might have stuff to do
        self.process_request_starts(request)
        # handle the request
        ishandled = self.routemanager.process_request(self, request)
        # after we end a request we might have stuff to do
        self.process_request_ends(request)
        # return whether we handled it
        return ishandled





    def process_request_starts(self, request):
        """
        Do stuff before processing a request
        """
        self.dbmanager.process_request_starts(request)


    def process_request_ends(self, request):
        """
        Do stuff before processing a request
        """
        self.dbmanager.process_request_ends(request)







# these just shortcut to assetmanager

    def resolve(self, text):
        return self.assetmanager.resolve(text)

    def absolute_filepath(self, relpath):
        return self.assetmanager.absolute_filepath(relpath)

    def absolute_url(self, relpath):
        return self.assetmanager.absolute_url(relpath)

    def relative_url(self, relpath):
        return self.assetmanager.relative_url(relpath)





















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
        outstr += self.logmanager.dumps(indent+1)
        outstr += "\n"
        outstr += self.dbmanager.dumps(indent+1)
        outstr += "\n"
        outstr += "\n"
        outstr += self.dispatcher.dumps(indent+1)
        outstr += "\n"
        outstr += self.registry.dumps(indent+1)
        outstr += "\n"
        outstr += self.templates.dumps(indent+1)
        outstr += "\n"
        outstr += self.packagemanager.dumps(indent+1)
        outstr += "\n"
        outstr += self.routemanager.dumps(indent+1)
        outstr += "\n"
        outstr += self.navnodes.dumps(indent+1)
        outstr += "\n"
        outstr += self.packagesettings.dumps(indent+1)
        outstr += "\n"
        outstr += self.templatehelper.dumps(indent+1)
        outstr += "\n"
        return outstr



