"""
msiteaddon_login.py
This file contains a siteaddon class for handling logins
"""


# mewlo imports
from mewlo.mpackages.core.siteaddon import msiteaddon
from mewlo.mpackages.core.navnode.mnav import NavNode, NavLink
from mewlo.mpackages.core.route.mroute import *
from mewlo.mpackages.core.controller.mcontroller import MewloController
from mewlo.mpackages.core.setting.msettings import MewloSettings

# python imports
import os, sys

# this is just a way to get the relative directory easily, and we use this in config settings
import controllers as pkgdirimp_controllers







class MewloSiteAddon_Login(msiteaddon.MewloSiteAddon):
    """
    The MewloSiteAddon_Login class adds routes, controllers, and views related to logging in, registering, etc.
    """



    def __init__(self):
        # call parent constructor
        super(MewloSiteAddon_Login, self).__init__()


    def startup(self, mewlosite):
        """
        Do preparatory stuff.
        """
        # call parent (this will call the add_* functions below).
        super(MewloSiteAddon_Login, self).startup(mewlosite)


    def shutdown(self):
        """Shutdown everything."""
        pass






























    def add_aliases(self):
        """create aliases."""
        # config some aliases we can use (for example in our templates)
        thisdir = os.path.abspath(os.path.dirname(__file__))
        aliases = {
            # add an alias so we can refer to our view path
            'addon_login_path': thisdir,
            }
        self.mewlosite.settings.merge_settings_key(MewloSettings.DEF_SECTION_aliases, aliases)




    def add_routes(self):
        """This is called by default by the base MewloSite near startup, to add routes to the system."""

        # create a routegroup
        routegroup = MewloRouteGroup()
        # overide the parent import-package-directory for the urls in this group? if we don't it will use the controller root set in SITE config
        routegroup.set_controllerroot(pkgdirimp_controllers)

        routegroup.append(
            MewloRoute(
                id = 'register',
                path = '/user/register',
                controller = MewloController(root=pkgdirimp_controllers, function='requests.request_register'),
                ))
        routegroup.append(
            MewloRoute(
                id = 'login',
                path = '/user/login',
                controller = MewloController(root=pkgdirimp_controllers, function='requests.request_login'),
                ))
        routegroup.append(
            MewloRoute(
                id = 'logout',
                path = '/user/logout',
                controller = MewloController(root=pkgdirimp_controllers, function='requests.request_logout'),
                ))

        # add routegroup we just created to the site
        self.mewlosite.routemanager.append(routegroup)




    def add_navnodes(self):
        """Create navigational structure for site pages."""

        # these are related to Routes above, except that NavNodes are like a hierarchical menu structure / site map, wheras Routes are flat patterns that map to controllers
        nodes = [
            NavNode('register', {
                'visible': lambda navnode,context: not context.get_value('isloggedin',False),
                'parent': 'site',
                'sortweight': 1.0,
                }),
            NavNode('login', {
                'visible': lambda navnode,context: not context.get_value('isloggedin',False),
                'parent': 'site',
                'sortweight': 8.0,
                }),
            NavNode('logout', {
                'menulabel': lambda navnode,context: "logout ({0})".format(context.get_value('username')),
                'menulabel_short': 'logout',
                'menuhint' : 'logout of your account',
                'visible': lambda navnode,context: context.get_value('isloggedin',False),
                'parent': 'site',
                'sortweight': 8.0,
                'pagetitle': 'Logout Page',
                }),
            ]

        # add nodes to site
        self.mewlosite.navnodes.add_nodes(nodes)




