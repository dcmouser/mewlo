"""
msiteaddon_group.py
This file contains a siteaddon class for handling group stuff
"""


# mewlo imports
from mewlo.mpacks.core.siteaddon import msiteaddon
from mewlo.mpacks.core.navnode.mnav import NavNode, NavLink
from mewlo.mpacks.core.route.mroute import *
from mewlo.mpacks.core.controller.mcontroller import MewloController
from mewlo.mpacks.core.setting.msettings import MewloSettings
from mewlo.mpacks.core.constants.mconstants import MewloConstants as mconst

# python imports
import os, sys

# our imports
import msiteaddon_group_manager

# this is just a way to get the relative directory easily, and we use this in config settings
import controllers as pkgdirimp_controllers







class MewloSiteAddon_Group(msiteaddon.MewloSiteAddon):
    """
    The MewloSiteAddon_Group class adds routes, controllers, and views related to groups
    """



    def __init__(self, mewlosite, debugmode):
        # call parent constructor
        super(MewloSiteAddon_Group, self).__init__(mewlosite, debugmode)
        # path prefix (used below in route setup)
        self.routepathprefix = '/groups'
        # namespaces
        self.namespace = 'group'
        # create the helper manager
        self.groupaddonmanager = self.mewlosite.createappendcomp('group_addon_manager', msiteaddon_group_manager.GroupAddonManager)




































    def add_aliases(self):
        """create aliases."""
        # config some aliases we can use (for example in our templates)
        thisdir = os.path.abspath(os.path.dirname(__file__))
        aliases = {
            # add an alias so we can refer to our view path
            'addon_path': thisdir,
            }
        self.mewlosite.merge_settings_aliases(aliases, namespace=self.namespace)



    def add_routes(self):
        """This is called by default by the base MewloSite near startup, to add routes to the system."""

        # create a routegroup
        routegroup = MewloRouteGroup(controllerroot = pkgdirimp_controllers, pathprefix=self.routepathprefix, namespace = self.namespace)

        # now add routes to it
        routegroup.append(
            MewloRoute(
                id = 'grouplist',
                path = '/list',
                controller = MewloController(root=pkgdirimp_controllers, function=self.groupaddonmanager.request_grouphome),
            ))
        routegroup.append(
            MewloRoute(
                id = 'groupinfo',
                path = '/info',
                controller = MewloController(root=pkgdirimp_controllers, function=self.groupaddonmanager.request_groupinfo),
                args = [
                    MewloRouteArgString(
                        id = 'id',
                        required = True,
                        help = "id of group",
                        ),
                    ],
            ))

        # add routegroup we just created to the site
        self.mewlosite.comp('routemanager').append(routegroup)






    def add_navnodes(self):
        """Create navigational structure for site pages."""

        # these are related to Routes above, except that NavNodes are like a hierarchical menu structure / site map, wheras Routes are flat patterns that map to controllers
        nodes = [
            NavNode('grouplist', {
                'menulabel': 'groups',
                'visible': True,
                'parent': 'site',
                'sortweight': 9.0,
                }),
            NavNode('groupinfo', {
                'visible': lambda navnode,context: navnode.isactive(context),
                'parent': 'grouplist',
                'sortweight': 9.0,
                'flag_linkurl': False,
                }),
            ]

        # add nodes to site
        self.mewlosite.comp('navnodemanager').add_nodes(nodes, namespace = self.namespace)
















