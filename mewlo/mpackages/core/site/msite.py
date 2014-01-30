"""
msite.py
This file contains classes to handle Mewlo site class.
"""


# mewlo imports
import msitemanager
from .. import mglobals
from ..helpers.dictlist import MDictList
from ..package import mpackagemanager
from ..route import mroute
from ..signal import msignal
from ..registry import mregistry
from ..setting.msettings import MewloSettings
from ..database import mdbsettings, mdbmanager_sqlalchemy, mdbmodel_settings, mdbmodel_gob
from ..rbac import mrbac
from ..navnode import mnav
from ..template import mtemplatehelper, mtemplate
from ..session import msessionmanager, msession
from ..verification import mverificationmanager, mverification
from ..asset import massetmanager
from ..eventlog import mlogger
from ..eventlog.mevent import Event, EventList, EWarning, EError, EDebug, EInfo
from ..eventlog.mlogger import MewloLogger
from ..eventlog.mlogtarget_file import MewloLogTarget_File
from ..helpers.misc import get_value_from_dict, resolve_expand_string
from ..user import muser
from ..group import mgroup
from ..rbac import mrbac
from ..siteaddon import msiteaddon




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
        self.isenabled = False
        self.siteurl_relative = ''
        # components
        self.components = MDictList()




        # setup log manager helper early so that log manager can receive messages
        self.createappendcomp('logmanager', mlogger.MewloLogManager)

        # now update site state
        self.set_state(MewloSettings.DEF_SITESTATE_INITIALIZE_START)

        # create (non-db-persistent) site settings -- these are set by configuration at runtime
        self.settings = self.createappendcomp('settings', MewloSettings)

        # component registry
        self.createappendcomp('registrymanager', mregistry.MewloRegistryManager)

        # signal dispatcher
        self.createappendcomp('signalmanager', msignal.MewloSignalManager)

        # database manager
        self.createappendcomp('dbmanager', mdbmanager_sqlalchemy.MewloDatabaseManagerSqlA)

        # rbac permission manager
        self.createappendcomp('rbacmanager', mrbac.MewloRbacManager)

        # create persistent(db) package settings
        self.packagesettings = self.createappendcomp('packagesettings', mdbsettings.MewloSettingsDb, MewloSettings.DEF_DBCLASSNAME_PackageSettings)

        # collection of mewlo addon packages
        self.createappendcomp('packagemanager', mpackagemanager.MewloPackageManager)

        # site addon manager
        self.createappendcomp('siteaddonmanager', msiteaddon.MewloSiteAddonManager)

        # route manager
        self.createappendcomp('routemanager', mroute.MewloRouteManager)

        # navnode manager
        self.createappendcomp('navnodemanager', mnav.NavNodeManager)

        # template manager
        self.createappendcomp('templatemanager', mtemplate.MewloTemplateManager)

        # assetmanager
        self.createappendcomp('assetmanager', massetmanager.MewloAssetManager)

        # template helper
        self.createappendcomp('templatehelper', mtemplatehelper.MewloTemplateHelper)

        # session helper
        self.createappendcomp('sessionmanager', msessionmanager.MewloSessionManager)

        # verification helper
        self.createappendcomp('verificationmanager', mverificationmanager.MewloVerificationManager)

        # update state
        self.set_state(MewloSettings.DEF_SITESTATE_INITIALIZE_END)




    def comp(self, componentname):
        return self.components.lookup(componentname)

    def appendcomp(self, componentname, component):
        self.components.append(componentname, component)
        return component

    def createappendcomp(self, componentname, componentclass, *args, **kwargs):
        component = componentclass(self, self.debugmode, *args, **kwargs)
        self.components.append(componentname, component)
        return component




    def get_isenabled(self):
        return self.isenabled

    def get_siteprefix(self):
        return self.siteprefix






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

        # any settings caching or other pre-preparation we need to do
        self.preprocess_settings(eventlist)
        # validate site settings first to make sure all is good
        self.validatesettings(eventlist)

        # now startup all site components
        self.startup_allcomponents(eventlist)

        # log all startup events
        self.logevents(eventlist)

        # update state
        self.set_state(MewloSettings.DEF_SITESTATE_STARTUP_END)

        # and return the eventlist
        return eventlist



    def startup_allcomponents(self, eventlist):
        """Startup all created helper manager components; note the order is important and is preserved from when we added."""

        # walk the component list
        for key,obj in self.components.get_tuplelist():
            # start up the component
            obj.startup(eventlist)
            # post startup
            obj.poststartup(eventlist)







    def shutdown(self, eventlist = None):
        """Shutdown everything."""

        # update state
        self.set_state(MewloSettings.DEF_SITESTATE_SHUTDOWN_START)

        # now shut down all site components
        self.shutdown_allcomponents()

        # update state (note this won't be logged since we will have shutdown log/db by now)
        self.set_state(MewloSettings.DEF_SITESTATE_SHUTDOWN_END)

        # done
        return eventlist



    def shutdown_allcomponents(self):
        """Shutdown all of our site components, in REVERSE order."""
        for key,obj in reversed(self.components.get_tuplelist()):
            obj.shutdown()

















    def ensure_earlydatabasemodels_mapped(self):
        """Some database models must be defined in early startup."""
        #modelclasslist = []
        #self.dbmanager.earlycreate_formodelclasslist(modelclasslist)
        pass












    def preprocess_settings(self, eventlist):
        """We may want to preprocess/cache some settings before we start."""
        # cache some stuff?
        self.controllerroot = self.settings.get_subvalue(MewloSettings.DEF_SECTION_config, MewloSettings.DEF_SETTINGNAME_controllerroot)
        # package manager settings
        self.comp('packagemanager').set_directories( self.get_root_package_directory_list() + self.get_site_package_directory_list() )
        self.comp('packagemanager').set_packagesettings( self.settings.get_value(MewloSettings.DEF_SECTION_packages) )
        self.comp('packagemanager').set_default_packagesettings(MewloSettings.DEF_SETTINGVAL_default_package_settings)
        self.comp('packagemanager').set_flag_loadsetuptoolspackages(self.settings.get_subvalue(MewloSettings.DEF_SECTION_config, MewloSettings.DEF_SETTINGNAME_flag_importsetuptoolspackages, MewloSettings.DEF_SETTINGVAL_flag_importsetuptoolspackages))
        # database manager settings
        self.comp('dbmanager').set_databasesettings( self.settings.get_value(MewloSettings.DEF_SECTION_database) )
        # isenabled flag
        self.isenabled = self.settings.get_subvalue(MewloSettings.DEF_SECTION_config, MewloSettings.DEF_SETTINGNAME_isenabled, self.isenabled)
        self.siteurl_relative = self.settings.get_subvalue(MewloSettings.DEF_SECTION_config, MewloSettings.DEF_SETTINGNAME_siteurl_relative, self.siteurl_relative)




    def validatesettings(self, eventlist=None):
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
                eventlist.append(EError(estr))
            else:
                eventlist.append(EWarning(estr))




























    def logevent(self, event, request = None, fields={}):
        """Shortcut to add a log message from an event/failure."""
        # convert it to an event if its just a plain string
        if (isinstance(event, basestring)):
            event = EDebug(event,fields=fields)
        # add request field (if it wasn't already set in mevent)
        if (request != None):
            missingfields = { 'request': request }
            event.mergemissings(missingfields)
        # log it
        self.comp('logmanager').process(event)


    def logevents(self, events, request = None):
        """Shortcut to add a log message from a *possible* iterable of events."""
        for event in events:
            self.logevent(event, request)










    def set_debugmode(self, val):
        """Set debugmode for the site, which may also have to pass on this value to components."""
        self.debugmode = val
        self.comp('logmanager').set_debugmode(val)

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
        self.add_earlydefault_settings()
        self.add_settings_early()
        self.add_latesettings_aliases()
        self.add_loggers()
        self.add_routes()
        self.add_navnodes()
        self.add_addons()
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

    def add_addons(self):
        """Does nothing in base class, but subclass can overide."""
        pass








    def merge_settings(self, settings):
        """Merge in some settings to our site settings."""
        self.settings.merge_settings(settings)


    def add_earlydefault_settings(self):
        """Set some default overrideable settings."""
        self.add_default_settings_config()
        self.add_default_settings_aliases()


    def add_default_settings_config(self):
        """Set default config settings."""
        config = {
            MewloSettings.DEF_SETTINGNAME_default_logfilename: MewloSettings.DEF_SETTINGVAL_default_logfilename_defaultvalue,
            }
        self.settings.merge_settings_key(MewloSettings.DEF_SECTION_config, config)


    def add_default_settings_aliases(self):
        """Set default alias settings."""
        aliases = {
            MewloSettings.DEF_SETTINGNAME_logfilepath: '${sitefilepath}/logging',
            MewloSettings.DEF_SETTINGNAME_dbfilepath: '${sitefilepath}/database',
            MewloSettings.DEF_SETTINGNAME_siteview_filepath: '${sitefilepath}/views',
            }
        self.settings.merge_settings_key(MewloSettings.DEF_SECTION_aliases, aliases)


    def add_latesettings_aliases(self):
        """Add some late aliases."""
        aliases = {
            MewloSettings.DEF_SETTINGNAME_siteurl_absolute: self.settings.get_subvalue(MewloSettings.DEF_SECTION_config, MewloSettings.DEF_SETTINGNAME_siteurl_absolute),
            MewloSettings.DEF_SETTINGNAME_siteurl_relative: self.settings.get_subvalue(MewloSettings.DEF_SECTION_config, MewloSettings.DEF_SETTINGNAME_siteurl_relative,''),
            MewloSettings.DEF_SETTINGNAME_sitefilepath: self.settings.get_subvalue(MewloSettings.DEF_SECTION_config, MewloSettings.DEF_SETTINGNAME_sitefilepath),
            MewloSettings.DEF_SETTINGNAME_sitename: self.settings.get_subvalue(MewloSettings.DEF_SECTION_config, MewloSettings.DEF_SETTINGNAME_sitename),
            }
        self.settings.merge_settings_key(MewloSettings.DEF_SECTION_aliases, aliases)
        self.alias_settings_change()


    def alias_settings_change(self):
        """Inform asset manager of new alias settings.  This *must* be called whenever alias settings may change."""
        self.comp('assetmanager').set_alias_settings(self.settings.get_value(MewloSettings.DEF_SECTION_aliases))








    def add_logger(self, logger):
        """Just ask the logmanager to add the logger."""
        self.comp('logmanager').add_logger(logger)
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
        # if the site is disabled, then it's like it's invisible, so it's not a match for this site
        if (not self.get_isenabled()):
            return False

        # if the request does not match site prefix, then it's not a match for this site
        if (not self.request_match_siteprefix(request)):
            return False;

        # ok, looks like it was meant for us

        # before we start a request we might have stuff to do
        self.process_request_starts(request)

        # log it
        #self.logevent(EInfo("Request URL: {0} from {1}.".format(request.get_fullurlpath_original(), request.get_remote_addr())),request=request)
        self.logevent(EInfo("Request URL: {0} from {1}.".format(request.get_fullurlpath_original(), request.get_remote_addr())))

        # handle the request
        ishandled = self.comp('routemanager').process_request(self, request)

        # after we end a request we might have stuff to do (this might include, for example, flushing the database)
        self.process_request_ends(request, ishandled)

        # return whether we handled it
        return ishandled











































    def request_match_siteprefix(self, request):
        """See if the request matches the prefix for this site (which could be blank)."""
        if (self.siteurl_relative == ''):
            return True
        # check (and strip) site prefx
        return request.preprocess_siteprefix(self.siteurl_relative)





    def process_request_starts(self, request):
        """
        Do stuff before processing a request
        """
        pass


    def process_request_ends(self, request, ishandled):
        """
        Do stuff before processing a request
        """
        if (ishandled):
            self.comp('dbmanager').process_request_ends(request)







# these just shortcut to assetmanager

    def resolve(self, text):
        return self.comp('assetmanager').resolve(text)

    def absolute_filepath(self, relpath):
        return self.comp('assetmanager').absolute_filepath(relpath)

    def absolute_url(self, relpath):
        return self.comp('assetmanager').absolute_url(relpath)

    def relative_url(self, relpath):
        return self.comp('assetmanager').relative_url(relpath)



















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
        outstr += " "*indent + "Site settings validation:\n"
        outstr += (self.validatesettings()).dumps(indent+1)
        outstr += "\n"
        outstr += self.components.dumps(indent)
        return outstr








    def is_readytoserve(self):
        """Check if there were any site prep errors, OR if any packages report they are not ready to run (need update, etc.)."""
        isreadytoserve = True
        if (not self.comp('packagemanager').is_readytoserve()):
            isreadytoserve = False
        return isreadytoserve

















    def updatecheck(self):
        """
        Check all packages for updates.  The packages themselves will store details about update check results.
        Note this covers not just web updates available, but database updates needed.
        """
        self.comp('packagemanager').updatecheck_allpackages()


    def updaterun(self):
        """
        Check all packages for updates.  The packages themselves will store details about update check results.
        Note this covers not just web updates available, but database updates needed.
        """
        self.comp('packagemanager').updaterun_allpackages()



    def get_allpackage_events(self):
        """
        Get combined eventlist for all packages on sites
        """
        return self.comp('packagemanager').get_allpackage_events()




