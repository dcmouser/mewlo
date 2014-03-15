"""
msite.py
This file contains classes to handle Mewlo site class.
"""


# mewlo imports
import msitemanager
from .. import mglobals
from ..helpers.dictlist import MDictList
from ..pack import mpackmanager
from ..route import mroute
from ..signal import msignal
from ..registry import mregistry
from ..setting.msettings import MewloSettings
from ..database import mdbsettings, mdbsettings_pack
from ..database import mdbmanager_sqlalchemy, mdbmodel_settings, mdbmodel_gob
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
from ..eventlog import mewloexception
from ..helpers.misc import get_value_from_dict, resolve_expand_string
from ..user import muser, musermanager
from ..group import mgroup, mgroupmanager
from ..rbac import mrbac
from ..siteaddon import msiteaddon
from ..mail import mmailmanager
from ..helpers import cfgmodule
from ..cache import mcache
from ..constants.mconstants import MewloConstants as mconst


# python imports
import os
from datetime import datetime, date, time











class MewloSite(object):
    """
    The MewloSite class represents a single "site" that handles requests.
    Typically you will only have one site running.
    """



    def __init__(self, sitemodulename, debugmode, commandlineargs=None, defaultconfigname=None):
        # Nothing that could fail should be done in this __init__ -- save that for later functions

        # save debugmode and commandline args
        self.debugmode = debugmode
        self.commandlineargs = commandlineargs

        # keep track of what stage we are in for testing, etc.
        self.startup_prep_stage = None
        self.site_stage = None

        # set global variable (not currently used)
        mglobals.set_mewlosite(self)

        # some defaults which will be overridden by settings
        self.sitename = self.__class__.__name__
        self.siteurl_relative = ''

        # record pack of the site for relative imports
        self.sitemodulename = sitemodulename

        # init misc. settings
        self.sitemanager = None
        self.controllerroot = None
        self.fallbacklogger = None
        self.isenabled = False

        # config name and helper
        self.configname = self.get_commandlinearg('config',defaultconfigname)
























    def create_allcomponents(self):
        """Create all the various components we uses."""

        # we store all components in a list/hash which we iterate for startup/shutdown/dumps debugging, and which can be used to lookup components
        self.components = MDictList()

        # setup log manager helper early so that log manager can receive messages (and queue them until startup)
        self.createappendcomp('logmanager', mlogger.MewloLogManager)

        # now update site state (log manager should catch this)
        self.set_site_stage(mconst.DEF_SITESTAGE_INITIALIZE_START)

        # create (non-db-persistent) site settings -- these are set by configuration at runtime
        self.settings = self.createappendcomp('settings', MewloSettings)

        # database manager
        self.createappendcomp('dbmanager', mdbmanager_sqlalchemy.MewloDatabaseManagerSqlA)

        # component registry
        self.createappendcomp('registrymanager', mregistry.MewloRegistryManager)

        # signal dispatcher
        self.createappendcomp('signalmanager', msignal.MewloSignalManager)

        # rbac permission manager
        self.createappendcomp('rbacmanager', mrbac.MewloRbacManager)

        # create persistent(db) pack settings
        self.createappendcomp('packsettings', mdbsettings_pack.MewloSettingsDb_Pack)

        # collection of mewlo addon packs
        self.createappendcomp('packmanager', mpackmanager.MewloPackManager)

        # site addon manager
        #self.createappendcomp('siteaddonmanager', msiteaddon.MewloSiteAddonManager)

        # route manager
        self.createappendcomp('routemanager', mroute.MewloRouteManager)

        # navnode manager
        self.createappendcomp('navnodemanager', mnav.NavNodeManager)

        # template manager
        self.createappendcomp('templatemanager', mtemplate.MewloTemplateManager)

        # asset and alias manager
        self.createappendcomp('assetmanager', massetmanager.MewloAssetManager)

        # template helper (this is available inside template/views and provides helper functions like navigation menus, etc.)
        self.createappendcomp('templatehelper', mtemplatehelper.MewloTemplateHelper)

        # session manager
        self.createappendcomp('sessionmanager', msessionmanager.MewloSessionManager)

        # verification manager
        self.createappendcomp('verificationmanager', mverificationmanager.MewloVerificationManager)

        # user manager
        self.createappendcomp('usermanager', musermanager.MewloUserManager)

        # group manager
        self.createappendcomp('groupmanager', mgroupmanager.MewloGroupManager)

        # mail manager
        self.createappendcomp('mailmanager', mmailmanager.MewloMailManager)

        # cache manager
        cachemanager = self.createappendcomp('cachemanager', mcache.MewloCacheManager_DogPile)






















































    def startup(self, eventlist = None):
        """
        Do preparatory stuff after settings have been set.
        It is critical that this function get called prior to running the system.
        """

        # now startup all site components
        self.startup_prep_allcomponents(eventlist)

        # and return the eventlist
        return eventlist





    def startup_prep_allcomponents(self, eventlist):
        """Loop through all startup stages and invoke all components (and ourself)."""
        finishedstages = []
        desiredstages = {}
        for stageid in mconst.DEF_STARTUPSTAGE_LISTALL:
            # invole all of our components that want this stage
            self.set_startup_prep_stage(stageid)
            component_tuples = self.components.get_tuplelist()
            for (key, obj) in component_tuples:
                if (not key in desiredstages):
                    # get the desired stages for the component since we haven't gotten it yet (this can happen later if the component is newly added)
                    desiredstages[key] = obj.get_startup_stages_needed()
                    if (not desiredstages[key]):
                        self.logevent("Component {0} reports it does not need any startup prep.".format(key))
                    else:
                        # now we check if this component wants stages we already completed, and error if so
                        missedstages = list(set(finishedstages) & set(desiredstages[key]))
                        #print "ATTN: GOT DESIRED FOR {0}: {1} - with missed = {2}".format(key,str(desiredstages[key]), str(missedstages))
                        if (missedstages):
                            raise Exception("Component {0} wants startup_prep for stage(s) [{1}] but was created AFTER that startup stage completed (during stage '{2}').".format(key, str(missedstages), stageid))
                # if this component wants this stage, invoke it
                if (stageid in desiredstages[key]):
                    # invoke it and log it
                    self.logevent("Component {0} - running startup_prep stage '{1}'.".format(key, stageid))
                    obj.startup_prep(stageid, eventlist)
                    # and REMOVE the stageid from desired list for this component
                    desiredstages[key].remove(stageid)
            # not invoke OURSELVES on this stage
            self.startup_prep(stageid, eventlist)
            # after we ran all components through a stage, mark that stage as complete (this helps us detect when a NEWLY added component missed a stage).
            finishedstages.append(stageid)



    def set_startup_prep_stage(self, stageid):
        """We keep track of which startup_prep stage we are in, in case we need to check it from other functions; this can be useful for detecting actions that should not be called after a certain stage."""
        self.startup_prep_stage = stageid
        self.set_site_stage('startup.{0}'.format(stageid))

    def set_site_stage(self, stageid):
        self.site_stage = stageid
	if (self.get_debugmode()):
	    print "ATTN:DEBUG Beginning site site stage: '{0}'.".format(stageid)
	    self.logevent("Beginning site site stage: '{0}'.".format(stageid))


    def get_startup_prep_stage(self):
        """Return current startup prep_stage."""
        return self.startup_prep_stage
    def get_startup_prep_stage_index(self):
        """Return current startup prep_stage."""
        return self.get_startup_prep_stage_index_from_stageid(self.startup_prep_stage)

    def get_startup_prep_stage_index_from_stageid(self, stageid):
        """Return index of a stageid string."""
        if (stageid==None):
            return -1
        return mconst.DEF_STARTUPSTAGE_LISTALL.index(stageid)

    def check_startup_prep_stagerange(self, minstageid, maxstageid):
        """Throw an exception if we are not within stage range."""
        curstageindex = self.get_startup_prep_stage_index()
        minstageid_index = get_startup_prep_stage_index_from_stageid(minstageid)
        maxstageid_index = get_startup_prep_stage_index_from_stageid(maxstageid)
        if ((minstageid_index > -1) and (curstageindex<minstageid_index)):
            raise Exception("Startup_prep stage is too low for current operation ({0} -- needs to be at least {1}).".format(get_startup_prep_stage(), minstageid))
        if ((maxstageid_index > -1) and (curstageindex>maxstageid_index)):
            raise Exception("Startup_prep stage is too high for current operation ({0} -- needs to be at most {1}).".format(get_startup_prep_stage(), maxstageid))



















    def startup_prep(self, stageid, eventlist):
        """Site has startup stuff it runs in different stages just like other components."""
        if (stageid == mconst.DEF_STARTUPSTAGE_sitepreinit):
            # early prep
            # we log errors/warnings to an eventlist and return it; either one we are passed or we create a new one if needed
            if (eventlist == None):
                eventlist = EventList()
            # any settings caching or other pre-preparation we need to do
            self.preprocess_settings(eventlist)
            # validate site settings first to make sure all is good
            self.validatesettings(eventlist)
        elif (stageid == mconst.DEF_STARTUPSTAGE_sitebuildmodels):
            # all database models have been registered with the system, finalize creation of models -- create all db tables, etc
            self.build_db_tablesandmappers()
        elif (stageid == mconst.DEF_STARTUPSTAGE_sitepostinit):
            # after other components are done
            # log all startup events
            self.logevents(eventlist)
            # commit any pending db stuff (normally we commit after each request)
            self.comp('dbmanager').commit_all_dbs()




























































































    def shutdown(self, eventlist = None):
        """Shutdown everything."""

        # update state
        self.set_site_stage(mconst.DEF_SITESTAGE_SHUTDOWN_START)

        # now shut down all site components
        self.shutdown_allcomponents()

        # update state (note this won't be logged since we will have shutdown log/db by now)
        self.set_site_stage(mconst.DEF_SITESTAGE_SHUTDOWN_END)

        # done
        return eventlist



    def shutdown_allcomponents(self):
        """Shutdown all of our site components, in REVERSE order."""
        for key,obj in reversed(self.components.get_tuplelist()):
            obj.shutdown()




























































    def build_db_tablesandmappers(self):
	"""It's time to build all registered models and database tables, etc."""
	self.comp('dbmanager').create_tableandmapper_forallmodelclasses()









    def preprocess_settings(self, eventlist):
        """
        This function is used to preprocess/cache some settings before we start.
        This function is called early in the startup() function.
        """

        # cache some stuff?
        self.controllerroot = self.settings.get_subvalue(mconst.DEF_SETTINGSEC_config, mconst.DEF_SETTINGNAME_controllerroot)
        # pack manager settings
        self.comp('packmanager').set_directories( self.get_root_pack_directory_list() + self.get_site_pack_directory_list() )
        self.comp('packmanager').set_packsettings( self.settings.get_value(mconst.DEF_SETTINGSEC_packs) )
        self.comp('packmanager').set_default_packsettings(mconst.DEF_SETTINGVAL_default_pack_settings)
        self.comp('packmanager').set_flag_loadsetuptoolspacks(self.settings.get_subvalue(mconst.DEF_SETTINGSEC_config, mconst.DEF_SETTINGNAME_flag_importsetuptoolspacks, mconst.DEF_SETTINGVAL_flag_importsetuptoolspacks))
        # database manager settings
        self.comp('dbmanager').set_databasesettings( self.settings.get_value(mconst.DEF_SETTINGSEC_database) )
        # isenabled flag
        self.isenabled = self.settings.get_subvalue(mconst.DEF_SETTINGSEC_config, mconst.DEF_SETTINGNAME_isenabled, self.isenabled)
        self.siteurl_relative = self.settings.get_subvalue(mconst.DEF_SETTINGSEC_config, mconst.DEF_SETTINGNAME_siteurl_relative, self.siteurl_relative)




    def validatesettings(self, eventlist=None):
        """
        Validate settings and return an EventList with errors and warnings.
        This function is called early in the startup() function, after preprocess_settings().
        """
        if (eventlist == None):
            eventlist = EventList()
        #
        self.validate_setting_config(eventlist, mconst.DEF_SETTINGNAME_pkgdirimps_sitempacks, False, "no directory will be scanned for site-specific extensions.")
        self.validate_setting_config(eventlist, mconst.DEF_SETTINGNAME_controllerroot, False, "no site-default specified for controller root.")
        # required stuff
        self.validate_setting_config(eventlist, mconst.DEF_SETTINGNAME_siteurl_relative, True, "site has no relative url specified; assumed to start at root (/).")
        self.validate_setting_config(eventlist, mconst.DEF_SETTINGNAME_siteurl_absolute, True, "site has no absolute url address.")
        self.validate_setting_config(eventlist, mconst.DEF_SETTINGNAME_sitefilepath, True, "site has no filepath specified for its home directory.")
        self.validate_setting_config(eventlist, mconst.DEF_SETTINGNAME_replacemirrorpath, True, "site has no filepath specified for its replacemirrore directory.")

        # return events encountered
        return eventlist


    def validate_setting_config(self, eventlist, varname, iserror, messagestr):
        """Helper function for the validate() method."""
        if (not self.settings.value_exists(mconst.DEF_SETTINGSEC_config, varname)):
            estr = "In site '{0}', site config variable '{1}' not specified; {2}".format(self.get_sitename(),varname,messagestr)
            if (iserror):
                eventlist.append(EError(estr))
            else:
                eventlist.append(EWarning(estr))







    def get_settingval(self, sectionname, valuename, defaultval=None):
        """Return a settings value."""
        return self.settings.get_subvalue(sectionname, valuename, defaultval)

    def get_settingsection(self, sectionname):
        """Return a settings value."""
        return self.settings.get_value(sectionname, [])


















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
























    def comp(self, componentname):
        """Shortcut to look up a component."""
        retv = self.components.lookup(componentname)
        if (retv == None):
            raise Exception("Component not found: '{0}'.".format(componentname))
        return retv

    def appendcomp(self, componentname, component):
        """Shortcut to append an already created component."""
        self.components.append(componentname, component)
        #print "ATTN:DEBUG in site appendcomp({0}).".format(componentname)
        return component

    def createappendcomp(self, componentname, componentclass, *args, **kwargs):
        """Shortcut to create and then append a component by class."""
        component = componentclass(self, self.debugmode, *args, **kwargs)
        self.appendcomp(componentname, component)
        return component






    def get_isenabled(self):
        """Simple accessor for isenabled flag."""
        return self.isenabled

    def get_siteprefix(self):
        """Simple accessor for site prefix (defines a prefix for the url of the site)."""
        return self.siteprefix


    def set_debugmode(self, val):
        """Set debugmode for the site, which may also have to pass on this value to components."""
        self.debugmode = val
        self.comp('logmanager').set_debugmode(val)

    def get_debugmode(self):
        """Return the debubmode."""
        return self.debugmode




    def get_sitename(self):
        """Simple accessor."""
        return self.sitename

    def get_id(self):
        """
        The get_id() function is a generic one that we use in several places where we have a hierarchy of objects (for example routegroups).
        Introspection will cause it to be used when displaying debug information.
        """
        return self.get_sitename()


    def set_sitemanager(self, sitemanager):
        """Set sitemanager reference."""
        self.sitemanager = sitemanager

    def get_controllerroot(self):
        """Simple accessor."""
        return self.controllerroot

    def get_sitemodulename(self):
        """Return import of ourself; useful for relative importing."""
        return self.sitemodulename

    def get_installdir(self):
        """Get the directory path of the mewlo installation from the mewlo pack."""
        import mewlo
        path = os.path.dirname(os.path.realpath(mewlo.__file__))
        return path

    def get_root_pack_directory_list(self):
        """Return a list of directories in the base/install path of Mewlo, where addon packs should be scanned"""
        basedir = self.get_installdir()
        packdirectories = [basedir + '/' + dir for dir in mconst.DEF_PACK_subdirlist]
        return packdirectories


    def get_site_pack_directory_list(self):
        """Return a list of absolute directory paths where (addon) packs should be scanned"""
        packdirectories = []
        sitepacks = self.settings.get_subvalue(mconst.DEF_SETTINGSEC_config, mconst.DEF_SETTINGNAME_pkgdirimps_sitempacks)
        if (sitepacks == None):
            pass
        else:
            for sitepack in sitepacks:
                if (isinstance(sitepack, basestring)):
                    # it's a string, use it directly
                    packpath = sitepack
                else:
                    # it's a module import, get it's directory
                    packpath = os.path.dirname(os.path.realpath(sitepack.__file__))
                # add path string to our list
                packdirectories.append(packpath)
        #
        return packdirectories


    def get_pkgdirimp_dotpathprefix_site(self):
        """Return import of ourself; useful for relative importing."""
        from string import join
        modpath = self.sitemodulename
        dirpath = join(modpath.split('.')[:-1], '.')
        return dirpath


    def is_readytoserve(self):
        """Check if there were any site prep errors, OR if any packs report they are not ready to run (need update, etc.)."""
        isreadytoserve = True
        if (not self.comp('packmanager').is_readytoserve()):
            isreadytoserve = False
        return isreadytoserve























































    def setup_early(self):
        """
        Do early setup stuff.  Most of the functions invoked here are empty and are intended for subclasses to override.
        This function is called by MewloSiteManager, right after site object is instantiated, before startup()
        """

        # create all helper/manager components first
        self.create_allcomponents()

        # set up config stuff
        self.setup_confighelper()

        # settings
        self.add_earlydefault_settings()
        self.add_settings_early()
        self.add_latesettings_aliases()
        self.add_latesettings_assets()

        # other stuff
        self.add_loggers()
        self.add_routes()
        self.add_navnodes()

        # site addons
        self.add_addons()

        # we add fallback loggers at END, after user-site added loggers
        self.add_fallback_loggers()

        # now update site state (log manager should catch this)
        self.set_site_stage(mconst.DEF_SITESTAGE_INITIALIZE_END)





    def setup_confighelper(self):
        """The DEFAULT configname should have been set ."""
        self.cfghelper = cfgmodule.MCfgModule()
        self.cfghelper.load_configfiles(self.configname, self.get_pkgdirimp_config())


    def add_earlydefault_settings(self):
        """Set some default overrideable settings."""
        self.add_default_settings_config()
        self.add_default_settings_aliases()


    def add_settings_early(self):
        """Does nothing in base class, but subclass can overide."""
        pass


    def add_latesettings_aliases(self):
        """Add some late aliases."""
        self.add_latedefault_aliases()


    def add_latedefault_aliases(self):
        """Add some late aliases."""
        aliases = {
            mconst.DEF_SETTINGNAME_siteurl_absolute: self.settings.get_subvalue(mconst.DEF_SETTINGSEC_config, mconst.DEF_SETTINGNAME_siteurl_absolute),
            mconst.DEF_SETTINGNAME_siteurl_relative: self.settings.get_subvalue(mconst.DEF_SETTINGSEC_config, mconst.DEF_SETTINGNAME_siteurl_relative,''),
            mconst.DEF_SETTINGNAME_sitefilepath: self.settings.get_subvalue(mconst.DEF_SETTINGSEC_config, mconst.DEF_SETTINGNAME_sitefilepath),
            mconst.DEF_SETTINGNAME_sitename: self.settings.get_subvalue(mconst.DEF_SETTINGSEC_config, mconst.DEF_SETTINGNAME_sitename),
            mconst.DEF_SETTINGNAME_mewlofilepath: self.get_installdir(),
            }
        self.settings.merge_settings_key(mconst.DEF_SETTINGSEC_aliases, aliases)
        self.alias_settings_change()


    def add_latesettings_assets(self):
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


    def add_fallback_loggers(self):
        """Create any default fallback loggers that we should always put in place."""
        # We create a fallback default file logger that will log everything from current run to file, and reset each run
        # ATTN:TODO - we will want to later change this to logrotate or something

        # create a single logger (with no filters); multiple loggers are supported because each logger can have filters that define what this logger filters out
        self.fallbacklogger = self.add_logger(MewloLogger('FallbackLogger'))

        # now add some targets (handlers) to it
        fpath = self.settings.get_subvalue(mconst.DEF_SETTINGSEC_config, mconst.DEF_SETTINGNAME_default_logfilename)
        self.fallbacklogger.add_target(MewloLogTarget_File(filename=self.resolve(fpath), filemode='w'))

















    def add_default_settings_config(self):
        """Set default config settings."""
        config = {
            mconst.DEF_SETTINGNAME_default_logfilename: mconst.DEF_SETTINGVAL_default_logfilename_defaultvalue,
            }
        self.settings.merge_settings_key(mconst.DEF_SETTINGSEC_config, config)


    def add_default_settings_aliases(self):
        """Set default alias settings."""
        aliases = {
            mconst.DEF_SETTINGNAME_logfilepath: '${sitefilepath}/logging',
            mconst.DEF_SETTINGNAME_dbfilepath: '${sitefilepath}/database',
            mconst.DEF_SETTINGNAME_siteview_filepath: '${sitefilepath}/views',
            }
        self.settings.merge_settings_key(mconst.DEF_SETTINGSEC_aliases, aliases)



















    def merge_settings(self, settings):
        """Merge in some settings to our site settings."""
        self.settings.merge_settings(settings)


    def alias_settings_change(self):
        """Inform asset manager of new alias settings.  This *must* be called whenever alias settings may change."""
        self.comp('assetmanager').set_alias_settings(self.settings.get_value(mconst.DEF_SETTINGSEC_aliases))


    def add_logger(self, logger):
        """Just ask the logmanager to add the logger."""
        self.comp('logmanager').add_logger(logger)
        return logger










































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
        if (not self.does_request_match_siteprefix(request)):
            return False;

        # ok, looks like it was meant for us

        # before we start a request we might have stuff to do
        self.process_request_starts(request)

        # log it
        #self.logevent(EInfo("Request URL: {0} from {1}.".format(request.get_fullurlpath_original(), request.get_remote_addr())),request=request)
        self.logevent(EInfo("Request URL: {0} from {1}.".format(request.get_fullurlpath_original(), request.get_remote_addr())))

        # handle the request
        try:
            ishandled = self.comp('routemanager').process_request(self, request)
        except mewloexception.MewloException_Web as exp:
            # we got a web exception, so we can convert that to a response
            ishandled = True
            self.process_mewloexception_web_response(request, exp)

        # after we end a request we might have stuff to do (this might include, for example, flushing the database)
        self.process_request_ends(request, ishandled)

        # return whether we handled it
        return ishandled






























    def process_mewloexception_web_response(self, request, exp):
        """A MewloWeb exception was thrown by controller -- we can generate a page in response to this."""
        # ATTN: to improve
        if (exp.flag_dorender):
            viewfilepath = '${siteviewpath}/generic_exception.jn2'
            request.add_pagemessage({'cls':'error','msg':str(exp)})
            request.response.render_from_template_file(viewfilepath)
            # clear flag
            exp.flag_dorender = False











    def does_request_match_siteprefix(self, request):
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

    def resolve_filepath(self, text):
        return self.comp('assetmanager').resolve_filepath(text)

    def absolute_filepath(self, relpath):
        return self.comp('assetmanager').absolute_filepath(relpath)

    def absolute_url(self, relpath):
        return self.comp('assetmanager').absolute_url(relpath)

    def relative_url(self, relpath):
        return self.comp('assetmanager').relative_url(relpath)
























    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = " "*indent + "MewloSite (" + self.__class__.__name__ + ") reporting in.\n"
        indent += 1
        outstr += " "*indent + "Using commandline = {0}.\n".format(str(self.commandlineargs))
        outstr += " "*indent + "Using siteconfigname = '{0}'.\n".format(self.configname)
        outstr += " "*indent + "Site settings validation:\n"
        outstr += (self.validatesettings()).dumps(indent+1)
        outstr += "\n"
        # dumps all components
        outstr += self.components.dumps('SITE COMPONENT ', indent, True)
        return outstr























    def updatecheck(self):
        """
        Check all packs for updates.  The packs themselves will store details about update check results.
        Note this covers not just web updates available, but database updates needed.
        """
        self.comp('packmanager').updatecheck_allpacks()


    def updaterun(self):
        """
        Check all packs for updates.  The packs themselves will store details about update check results.
        Note this covers not just web updates available, but database updates needed.
        """
        self.comp('packmanager').updaterun_allpacks()


    def get_allpack_events(self):
        """
        Get combined eventlist (report on update checking, etc.) for all packs on sites
        """
        return self.comp('packmanager').get_allpack_events()
























    def get_pkgdirimp_config(self):
        # returns the package directory import where config settings files live
        return None


    def get_commandlinearg(self, keyname, defaultval=None):
        """Get commandline arg or use default."""
        if (hasattr(self.commandlineargs,keyname)):
            val = getattr(self.commandlineargs,keyname)
            if (val != None):
                return val
        try:
            # try to access commandline args as dictionary
            return self.commandlineargs[keyname]
        except:
            pass
        # return default val
        return defaultval


    def get_configval(self, keyname, defaultval=None):
        """Get a value from the appropriate config file."""
        return self.cfghelper.get_value(keyname,defaultval)


    def run_configfunc(self, functionname, *args, **kwargs):
        """Run func in the appropriate config file(s)."""
        return self.cfghelper.run_func(functionname,*args, **kwargs)

    def run_allconfigfuncs(self, functionname, *args, **kwargs):
        """Run func in the appropriate config file(s)."""
        self.cfghelper.run_allfuncs(functionname,*args, **kwargs)









    def renderstr_from_template_file(self, templatefilepath, args=None):
        """Shortcut to render a template and set responsedata from it, passing response object to template as an extra arg."""
        template = self.comp('templatemanager').from_file(templatefilepath)
        return self.renderstr_from_template(template, args)

    def renderstr_from_template_string(self, templatestring, args=None):
        """Shortcut to render a template and set responsedata from it, passing response object to template as an extra arg."""
        template = self.comp('templatemanager').from_string(templatestring)
        return self.renderstr_from_template(template, args)

    def rendersections_from_template_file(self, templatefilepath, args=None, required_sections=[]):
        """Shortcut to render a template and set responsedata from it, passing response object to template as an extra arg."""
        template = self.comp('templatemanager').from_file(templatefilepath)
        return self.rendersections_from_template(template, args, required_sections)


    def renderstr_from_template(self, template, args=None):
        """Shortcut to return html for a template and set responsedata from it, passing response object to template as an extra arg."""
        renderedtext = template.render_string(args)
        return renderedtext

    def rendersections_from_template(self, template, args=None, required_sections=[]):
        """Shortcut to return dictionary of html for a template and set responsedata from it, passing response object to template as an extra arg."""
        renderedsections = template.render_sections(args, required_sections)
        return renderedsections



