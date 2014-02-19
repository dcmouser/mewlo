"""
msiteaddon_account.py
This file contains a siteaddon class for handling account creation/login
"""


# mewlo imports
from mewlo.mpacks.core.siteaddon import msiteaddon
from mewlo.mpacks.core.navnode.mnav import NavNode, NavLink
from mewlo.mpacks.core.route.mroute import *
from mewlo.mpacks.core.controller.mcontroller import MewloController
from mewlo.mpacks.core.setting.msettings import MewloSettings

# python imports
import os, sys

# this is just a way to get the relative directory easily, and we use this in config settings
import controllers as pkgdirimp_controllers







class MewloSiteAddon_Account(msiteaddon.MewloSiteAddon):
    """
    The MewloSiteAddon_Account class adds routes, controllers, and views related to logging in, registering, etc.
    """



    def __init__(self):
        # call parent constructor
        super(MewloSiteAddon_Account, self).__init__()
        # path prefix (used below in route setup)
        self.pathprefix = '/account'


    def startup(self, mewlosite):
        """
        Do preparatory stuff.
        """
        # call parent (this will call the add_* functions below).
        super(MewloSiteAddon_Account, self).startup(mewlosite)


    def shutdown(self):
        """Shutdown everything."""
        pass






























    def add_aliases(self):
        """create aliases."""
        # config some aliases we can use (for example in our templates)
        thisdir = os.path.abspath(os.path.dirname(__file__))
        aliases = {
            # add an alias so we can refer to our view path
            'addon_account_path': thisdir,
            }
        self.mewlosite.settings.merge_settings_key(MewloSettings.DEF_SECTION_aliases, aliases)




    def add_routes(self):
        """This is called by default by the base MewloSite near startup, to add routes to the system."""

        # create a routegroup
        routegroup = MewloRouteGroup()
        # overide the parent import-pack-directory for the urls in this group? if we don't it will use the controller root set in SITE config
        routegroup.set_controllerroot(pkgdirimp_controllers)
        routegroup.set_pathprefix(self.pathprefix)

        routegroup.append(
            MewloRoute(
                id = 'register',
                path = '/register',
                controller = MewloController(root=pkgdirimp_controllers, function='requests.request_register'),
            ))
        routegroup.append(
            MewloRoute(
                id = 'login',
                path = '/login',
                controller = MewloController(root=pkgdirimp_controllers, function='requests.request_login'),
            ))
        routegroup.append(
            MewloRoute(
                id = 'logout',
                path = '/logout',
                controller = MewloController(root=pkgdirimp_controllers, function='requests.request_logout'),
            ))
        routegroup.append(
            MewloRoute(
                id = 'verify_registration',
                path = '/verifyreg',
                args = [
                        MewloRouteArgString(
                            id = 'code',
                            required = True,
                            help = "verification code",
                            ),
                        ],
                controller = MewloController(root=pkgdirimp_controllers, function='requests.request_verify_registration'),              
            ))
        routegroup.append(        
            MewloRoute(
                id = 'register2',
                path = '/register2',
                controller = MewloController(root=pkgdirimp_controllers, function='requests.request_register2'),
            ))


        # add routegroup we just created to the site
        self.mewlosite.comp('routemanager').append(routegroup)




    def add_navnodes(self):
        """Create navigational structure for site pages."""

        # these are related to Routes above, except that NavNodes are like a hierarchical menu structure / site map, wheras Routes are flat patterns that map to controllers
        nodes = [
            NavNode('register', {
                'visible': lambda navnode,context: not (context.get_value('user').get_isloggedin()),
                'parent': 'site',
                'sortweight': 1.0,
                }),
            NavNode('login', {
                'visible': lambda navnode,context: not (context.get_value('user').get_isloggedin()),
                'parent': 'site',
                'sortweight': 8.0,
                }),
            NavNode('logout', {
                'menulabel': lambda navnode,context: "logout ({0})".format(context.get_value('user').get_username()),
                'menulabel_short': 'logout',
                'menuhint' : 'logout of your account',
                'visible': lambda navnode,context: context.get_value('user').get_isloggedin(),
                'parent': 'site',
                'sortweight': 8.0,
                'pagetitle': 'Logout Page',
                }),
            NavNode('verify_registration', {
                # this navigation node (menu) is not shown unless the user is actually on this page.  We use this for unusual pages.  Alternatively we could set visible false and visible_breadcrumb True to have nearly the same effect
                'visible': lambda navnode,context: navnode.isactive(context),
                # we also make the page menu a static text item, not a link
                'flag_linkurl': False,
                'parent': 'register',
                'sortweight': 8.0,
                }),
            NavNode('register2', {
                'visible': lambda navnode,context: navnode.isactive(context),
                'flag_linkurl': False,                
                'parent': 'register',
                'sortweight': 1.0,
                }),            
            ]

        # add nodes to site
        self.mewlosite.comp('navnodemanager').add_nodes(nodes)




