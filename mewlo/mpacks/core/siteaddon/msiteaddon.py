"""
siteaddon.py
This file contains bases classes for MewloSiteAddons
"""


# mewlo imports
from ..manager import manager








class MewloSiteAddon(manager.MewloManager):
    """
    The MewloSiteAddon class adds routes, controllers, and views
    """

    # class constants
    description = "A site addon is derived from MewloManager and represents an object that provides routes, controllers, navnonodes, etc."
    typestr = "siteaddon"


    def __init__(self, mewlosite, debugmode):
        """
        Initialization/construction of a manager
        When this happens you should never do much -- because you may have no idea what other managers/components have been created yet.
        """
        super(MewloSiteAddon, self).__init__(mewlosite, debugmode)


    def prestartup_1(self, eventlist):
        """
        This is called for all managers, before any managers get startup() called.
        By the time this gets called you can be sure that ALL managers/components have been added to the site.
        The most important thing is that in this function managers create and register any database classes BEFORE they may be used in startup.
        The logic is that all managers must register their database classes, then the database tables will be build, then we can proceed to startup.
        """
        super(MewloSiteAddon, self).prestartup_1(eventlist)


    def prestartup_2(self, eventlist):
        """
        This is called for all managers, before any managers get startup() called.
        By the time this gets called you can be sure that ALL managers/components have been added to the site.
        The most important thing is that in this function managers create and register any database classes BEFORE they may be used in startup.
        The logic is that all managers must register their database classes, then the database tables will be build, then we can proceed to startup.
        """
        super(MewloSiteAddon, self).prestartup_2(eventlist)
        # these used to be in startup()
        self.add_aliases()
        self.add_routes()
        self.add_navnodes()


    def startup(self, eventlist):
        """Startup everything."""
        super(MewloSiteAddon, self).startup(eventlist)
        #
        self.mewlosite.logevent("Startup of siteaddon ({0}).".format(self.__class__.__name__))


    def poststartup(self, eventlist):
        """Called after all managers finish with startup()."""
        super(MewloSiteAddon, self).poststartup(eventlist)



    def shutdown(self):
        """Shutdown everything, we are about to exit."""
        self.mewlosite.logevent("Shutdown of MewloSiteAddon ({0}).".format(self.__class__.__name__))
        pass


    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = " "*indent + "MewloSiteAddon ({0}) reporting in.\n".format(self.__class__.__name__)
        outstr += self.dumps_description(indent+1)
        return outstr



    def add_aliases(self):
        """create aliases."""
        pass

    def add_routes(self):
        """Add routes used by the site addon."""
        pass

    def add_navnodes(self):
        """Add navnodes used by the site addon."""
        pass




    def sitecomp_assetmanager(self):
        return self.mewlosite.comp('assetmanager')





















#class MewloSiteAddonManager(manager.MewloManager):
#    """
#    The MewloSiteAddonManager class manages a set of site addons
#    """
#
#    def __init__(self, mewlosite, debugmode):
#        super(MewloSiteAddonManager,self).__init__(mewlosite, debugmode)
#        self.siteaddons = []
#
#    def startup(self, eventlist):
#        super(MewloSiteAddonManager,self).startup(eventlist)
#        for siteaddon in self.siteaddons:
#            siteaddon.startup(self.mewlosite)
#
#    def shutdown(self):
#        super(MewloSiteAddonManager,self).shutdown()
#
#    def append(self, siteaddon):
#        """Append a new siteaddon (or list of routes) (or hierarchical routegroups) to our routes list."""
#        self.siteaddons.append(siteaddon)
#
#    def dumps(self, indent=0):
#        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
#        outstr = " "*indent + "MewloSiteAddonManager reporting in with {0} site addons registered:\n".format(len(self.siteaddons))
#        #outstr += " "*indent + " Routegroup: ers: " + str(self.controllerroot) + "\n"
#        for siteaddon in self.siteaddons:
#            outstr += siteaddon.dumps(indent+1)
#        return outstr



































