"""
siteaddon.py
This file contains bases classes for MewloSiteAddons
"""


# mewlo imports
from ..manager import manager








class MewloSiteAddon(object):
    """
    The MewloSiteAddon class adds routes, controllers, and views
    """



    def __init__(self):
        # Nothing that could fail should be done in this __init__ -- save that for later functions
        pass


    def startup(self, mewlosite):
        """
        Do preparatory stuff.
        """
        self.mewlosite = mewlosite
        #
        self.add_aliases()
        self.add_routes()
        self.add_navnodes()


    def shutdown(self):
        """Shutdown everything."""
        pass




    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = " "*indent + "MewloSiteAddon ({0}) reporting in.\n".format(self.__class__.__name__)
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


























class MewloSiteAddonManager(manager.MewloManager):
    """
    The MewloSiteAddonManager class manages a set of site addons
    """

    def __init__(self):
        super(MewloSiteAddonManager,self).__init__()
        self.siteaddons = []

    def startup(self, mewlosite, eventlist):
        super(MewloSiteAddonManager,self).startup(mewlosite,eventlist)
        for siteaddon in self.siteaddons:
            siteaddon.startup(mewlosite)


    def shutdown(self):
        super(MewloSiteAddonManager,self).shutdown()




    def append(self, siteaddon):
        """Append a new siteaddon (or list of routes) (or hierarchical routegroups) to our routes list."""
        self.siteaddons.append(siteaddon)





    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = " "*indent + "MewloSiteAddonManager reporting in with {0} site addons registered:\n".format(len(self.siteaddons))
        #outstr += " "*indent + " Routegroup: ers: " + str(self.controllerroot) + "\n"
        for siteaddon in self.siteaddons:
            outstr += siteaddon.dumps(indent+1)
        return outstr

