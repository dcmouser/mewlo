"""
settings.py
This file contains classes to support hierarchical settings.

We really don't do anything fancy here -- in fact some of it is a bit ugly and could use rewriting.

Essentially we are just maintaining a hierarchical dictionary with some support functions to ease access.

"""


# helper imports
import helpers.settings.settings as settings



class MewloSettings(settings.Settings):
    """
    The MewloSettings class stores a hierarchical dictionary of settings
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
    DEF_SETTINGNAME_siteviewfilepath = 'siteviewpath'
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
    #
    # database classes
    DEF_DBCLASSNAME_PackageSettings = 'DbModel_Settings_Package'
    DEF_DBTABLENAME_PackageSettings = 'settings_package'
    DEF_DBCLASSNAME_MainSettings = 'DbModel_Settings_Main'
    DEF_DBTABLENAME_MainSettings = 'settings_main'





    def __init__(self):
        # parent
        super(MewloSettings,self).__init__()


    def startup(self, mewlosite, eventlist):
        """Any initial startup stuff to do?"""
        self. mewlosite = mewlosite
        # parent
        super(MewloSettings,self).startup()


    def shutdown(self):
        """Shutdown"""
        # parent
        super(MewloSettings,self).shutdown()
