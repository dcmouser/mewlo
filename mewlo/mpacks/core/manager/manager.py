"""
manager.py

A base class for high-level site-helping managers.
"""

# mewlo imports
from ..constants.mconstants import MewloConstants as mconst




class MewloManager(object):
    """Base class for high-level site-helping managers; base class does little."""

    # class constants
    description = "Base MewloManager class"
    typestr = "No type information"


    def __init__(self, mewlosite, debugmode):
        """
        Initialization/construction of a manager
        When this happens you should never do much -- because you may have no idea what other managers/components have been created yet.
        """
        # settings
        self.mewlosite = mewlosite
        self.startup_stages_needed = []
        self.viewfiles = {}

    def needs_startupstages(self, stagelist):
        """Merge some startup stages."""
        # we want to eliminted duplicates so we use list(set())
        self.startup_stages_needed = list(set(self.startup_stages_needed + stagelist))

    def get_startup_stages_needed(self):
        """Return a list of startup stages needed by this component."""
        return self.startup_stages_needed


    def startup_prep(self, stageid, eventlist):
        """
        This is invoked by site strtup, for each stage specified in startup_stages_needed() above.
        """
        pass


    def get_settings_section(self):
        """Return the settings section used by this manager."""
        #ATTN: UNFINISHED -- for now we only use this for siteaddon managers
        return self.settings_section

    def set_settings_section(self, settings_section):
        self.settings_section = settings_section

    def get_settingval(self, settingname):
        """We and others can call this to ask for a setting value from us, using the initialized settings_section"""
        #ATTN: we may want to move this to manager
        self.mewlosite.get_settingval(self.get_settings_section(), settingname)




    def shutdown(self):
        """Shutdown everything, we are about to exit."""
        self.mewlosite.logevent("Shutdown of manager ({0}).".format(self.__class__.__name__))







    def get_description(self):
        return self.description
    def get_typestr(self):
        return self.typestr



    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr =  " "*indent + "MewloManager ({0}) reporting in:\n".format(self.__class__.__name__)
        outstr += self.dumps_description(indent+1)
        return outstr


    def dumps_description(self, indent=0):
        outstr = " "*indent + "Type: {0}.\n".format(self.get_typestr())
        outstr += " "*indent + "Description: {0}.\n".format(self.get_description())
        return outstr





    def get_mewlosite(self):
        return self.mewlosite

    def sitecomp_usermanager(self):
        return self.mewlosite.comp('usermanager')
    def sitecomp_groupmanager(self):
        return self.mewlosite.comp('groupmanager')
    def sitecomp_verificationmanager(self):
        return self.mewlosite.comp('verificationmanager')
    def sitecomp_mailmanager(self):
        return self.mewlosite.comp('mailmanager')
    def sitecomp_cachemanager(self):
        return self.mewlosite.comp('cachemanager')
    def sitecomp_rbacmanager(self):
        return self.mewlosite.comp('rbacmanager')
    def sitecomp_dbmanager(self):
        return self.mewlosite.comp('dbmanager')
    def sitecomp_routemanager(self):
        return self.mewlosite.comp('routemanager')
    def sitecomp_jsmanager(self):
        return self.mewlosite.comp('jsmanager')
    def sitecomp_hsmanager(self):
        return self.mewlosite.comp('hsmanager')
    def sitecomp_assetmanager(self):
        return self.mewlosite.comp('assetmanager')



    def get_setting_value(self, sectionmame, defaultval=None):
        return self.mewlosite.settings.get_value(sectionmame, defaultval)


    def get_setting_subvalue(self, sectionmame, varname, defaultval=None):
        return self.mewlosite.settings.get_subvalue(sectionmame, varname, defaultval)











    # originally in request helper (some of these require self.viewbasepath to be set)

    def set_renderpageid(self, request, pageid):
        """Helper function to set page id."""
        request.response.set_renderpageid(pageid)

    def set_renderpageid_ifnotset(self, request, pageid):
        """Helper function to set page id."""
        request.response.set_renderpageid_ifnotset(pageid)

    def calc_local_templatepath_byid(self, viewfileid):
        """Just simple wrapper that calls calc_localtemplatepath after looking up viewfilepath_byid."""
        return self.calc_localtemplatepath(self.lookup_viewfilepath_byid(viewfileid))

    def lookup_viewfilepath_byid(self, viewfileid):
        """Just simple wrapper around dictionary lookup."""
        return self.viewfiles[viewfileid]

    def calc_localtemplatepath(self, viewfilepath):
        """Just combine viewbasepath with filename."""
        return self.viewbasepath + '/' + viewfilepath

    def render_localview_byfilename(self, request, viewfilepath, args=None):
        """Helper function to render relative view file."""
        request.response.render_from_template_file(self.calc_localtemplatepath(viewfilepath), args=args)

    def render_localview_byid(self, request, viewfileid, args=None):
        """Helper function to render relative view file."""
        return self.render_localview_byfilename(request, self.lookup_viewfilepath_byid(viewfileid), args)