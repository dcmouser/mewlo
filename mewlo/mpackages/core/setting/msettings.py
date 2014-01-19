"""
settings.py
This file contains classes to support hierarchical settings.

We really don't do anything fancy here -- in fact some of it is a bit ugly and could use rewriting.

Essentially we are just maintaining a hierarchical dictionary with some support functions to ease access.

"""


# helper imports
from ..helpers.misc import get_value_from_dict



class MewloSettings(object):
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
    DEF_SETTINGNAME_siteurl_relative = 'siteurl_relative'
    DEF_SETTINGNAME_siteurl_absolute = 'siteurl_absolute'
    DEF_SETTINGNAME_sitefilepath = 'sitefilepath'
    DEF_SETTINGNAME_default_logfilename = 'logfilename'
    DEF_SETTINGNAME_logfilepath = 'logfilepath'
    DEF_SETTINGNAME_dbfilepath = 'dbfilepath'
    DEF_SETTINGNAME_siteview_filepath = 'siteviewpath'
    DEF_SETTINGNAME_sitename = 'sitename'
    DEF_SETTINGNAME_flag_importsetuptoolspackages = 'flag_importsetuptoolspackages'
    #
    DEF_SETTINGNAME_isenabled = 'isenabled'
    DEF_SETTINGNAME_isonline = 'isonline'
    DEF_SETTINGNAME_offline_mode = 'offline_mode'
    DEF_SETTINGNAME_offline_message = 'offline_message'
    DEF_SETTINGNAME_offline_allowadmin = 'offline_allowadmin'

    # default values
    DEF_SETTINGVAL_default_logfilename_defaultvalue = '${logfilepath}/mewlo.log'
    DEF_SETTINGVAL_default_package_settings = { 'enabled': False }
    DEF_SETTINGVAL_flag_importsetuptoolspackages = True
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
        self.settingdict = {}
        # init some sections, so we can get early references to them
        #self.settingdict[self.DEF_SECTION_aliases] = {}

    def startup(self, mewlosite, eventlist):
        """Any initial startup stuff to do?"""
        self. mewlosite = mewlosite

    def shutdown(self):
        """Shutdown"""


    def remove_all(self):
        """Clear contents of settings."""
        self.settingdict = {}

    def remove_key(self, keyname):
        """Clear contents of one key."""
        del self.settingdict[keyname]

    def remove_subkey(self, keyname, keysubname):
        """Clear contents of one key."""
        del self.settingdict[keyname][keysubname]


    def merge_settings(self, settingstoadd):
        """Just merge in a new dicitonary into our main dictionary."""
        self.settingdict.update(settingstoadd)



    def merge_settings_key(self, keyname, settingstoadd):
        """Merge in a new dicitonary into our main dictionary at a specific root section (creating root section if needed)."""
        if not keyname in self.settingdict:
            self.settingdict[keyname] = settingstoadd
        else:
            # merge the new settings with old, e.g. union of arrays or dictionaries, etc
            self.settingdict[keyname].update(settingstoadd)


    def merge_settings_subkey(self, keyname, subkeyname, settingstoadd):
        """Merge in a new dicitonary into our main dictionary at a specific root section (creating root section if needed)."""
        if not keyname in self.settingdict:
            self.settingdict[keyname] = {subkeyname: settingstoadd}
        elif not subkeyname in self.settingdict[keyname]:
            self.settingdict[keyname][subkeyname] = settingstoadd
        else:
            # merge the new settings with old, e.g. union of arrays or dictionaries, etc
            self.settingdict[keyname][subkeyname].update(settingstoadd)




    def set(self, newsettings):
        """Overwrite all."""
        #self.remove_all()
        #self.merge_settings(newsettings)
        self.settingdict = newsettings

    def update(self, newsettings):
        """Overwrite all."""
        self.settingdict.update(newsettings)

    def get(self):
        """Get all."""
        return self.settingdict


    def set_key(self, keyname, value):
        """Set and overwrite a value at a section, replacing whatever was there."""
        self.settingdict[keyname] = value


    def get_value(self, keyname, defaultval=None):
        """Lookup value from our settings dictionary and return it or default if not found."""
        return get_value_from_dict(self.settingdict, keyname, defaultval)


    def get_subvalue(self, keyname, keysubname, defaultval=None):
        """Lookup value from our settings dictionary at a certain root section, and return it or default if not found."""
        if (keyname in self.settingdict):
            if (keysubname in self.settingdict[keyname]):
                return self.settingdict[keyname][keysubname]
        return defaultval

    def get_subvalue_required(self, keyname, keysubname):
        """Lookup value from our settings dictionary at a certain root section, and return it or raise exception."""
        return self.settingdict[keyname][keysubname]


    def set_subvalue(self, keyname, keysubname, val):
        """Set propery sub value."""
        settingstoadd = {keysubname:val}
        self.merge_settings_key(keyname,settingstoadd)




    def get_subsubvalue(self, keyname, keysubname, keysubsubname, defaultval=None):
        """Lookup value from our settings dictionary at a certain root section, and return it or default if not found."""
        if (keyname in self.settingdict):
            if (keysubname in self.settingdict[keyname]):
                if (keysubsubname in self.settingdict[keyname][keysubname]):
                    return self.settingdict[keyname][keysubname][keysubsubname]
        return defaultval

    def set_subsubvalue(self, keyname, keysubname, keysubsubname, val):
        """Set propery sub value."""
        settingstoadd = {keysubsubname:val}
        self.merge_settings_subkey(keyname, keysubname, settingstoadd)
        #print "Aftering setting {0}.{1}.{2}".format(keyname,keysubname,keysubsubname) + " we have: "+str(self.settingdict)



    def value_exists(self, keyname, keysubname=None):
        """Return true if the item existing in our settings dictionary (at specific root section if specified)."""
        if (keysubname == None):
            return (keyname in self.settingdict)
        if (not keyname in self.settingdict):
            return False
        return (keysubname in self.settingdict[keyname])



    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = " "*indent + "Settings ({0}):\n".format(self.__class__.__name__)
        indent += 1
        outstr += " "*indent + str(self.settingdict)+"\n"
        return outstr

