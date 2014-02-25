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
        #
        routegroup.append(
            MewloRoute(
                id = 'register',
                path = '/register',
                controller = MewloController(root=pkgdirimp_controllers, function='requests.request_register'),
            ))
        routegroup.append(
            MewloRoute(
                id = 'register_deferred_verify',
                path = '/verifyreg',
                args = [
                        MewloRouteArgString(
                            id = 'code',
                            required = True,
                            help = "verification code",
                            ),
                        ],
                controller = MewloController(root=pkgdirimp_controllers, function='requests.request_deferred_verify'),
            ))
        #
        routegroup.append(
            MewloRoute(
                id = 'profile',
                path = '/profile',
                args = [
                        MewloRouteArgString(
                            id = 'userid',
                            required = False,
                            help = "id of user whose profile is being viewed",
                            ),
                        ],
                controller = MewloController(root=pkgdirimp_controllers, function='requests.request_profile'),
            ))
        #
        routegroup.append(
            MewloRoute(
                id = 'userfield_verify',
                path = '/fieldverify',
                args = [
                    MewloRouteArgString(
                        id = 'field',
                        required = True,
                        help = "field name being verified",
                        ),
                    MewloRouteArgString(
                        id = 'code',
                        required = True,
                        help = "verification code",
                        ),
                    ],
                controller = MewloController(root=pkgdirimp_controllers, function='requests.request_userfield_verify'),
            ))
        #
        routegroup.append(
            MewloRoute(
                id = 'resend_register_verification',
                path = '/resendverify',
                controller = MewloController(root=pkgdirimp_controllers, function='requests.resend_register_verification'),
            ))
        #
        routegroup.append(
            MewloRoute(
                id = 'send_reset_password',
                path = '/reqresetpassword',
                controller = MewloController(root=pkgdirimp_controllers, function='requests.send_reset_password'),
            ))
        routegroup.append(
            MewloRoute(
                id = 'reset_password',
                path = '/resetpassword',
                args = [
                    MewloRouteArgString(
                        id = 'code',
                        required = False,
                        help = "verification code",
                        ),
                    ],
                controller = MewloController(root=pkgdirimp_controllers, function='requests.reset_password'),
            ))
        #
        routegroup.append(
            MewloRoute(
                id = 'modify_field',
                path = '/modify',
                args = [
                    MewloRouteArgString(
                        id = 'field',
                        required = True,
                        help = "field name being verified",
                        ),
                    ],
                controller = MewloController(root=pkgdirimp_controllers, function='requests.modify_field'),
            ))
        routegroup.append(
            MewloRoute(
                id = 'login_bycode',
                path = '/loginby',
                args = [
                    MewloRouteArgString(
                        id = 'code',
                        required = False,
                        help = "verification code",
                        ),
                    ],
                controller = MewloController(root=pkgdirimp_controllers, function='requests.login_bycode'),
            ))


        # add routegroup we just created to the site
        self.mewlosite.comp('routemanager').append(routegroup)






    def add_navnodes(self):
        """Create navigational structure for site pages."""

        # these are related to Routes above, except that NavNodes are like a hierarchical menu structure / site map, wheras Routes are flat patterns that map to controllers
        nodes = [
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
            #
            NavNode('register', {
                'visible': lambda navnode,context: not (context.get_value('user').get_isloggedin()),
                'parent': 'site',
                'sortweight': 1.0,
                }),
            NavNode('register_deferred_verify', {
                'menulabel': 'verify registration',
                # this navigation node (menu) is not shown unless the user is actually on this page.  We use this for unusual pages.  Alternatively we could set visible false and visible_breadcrumb True to have nearly the same effect
                'visible': lambda navnode,context: navnode.isactive(context),
                # we also make the page menu a static text item, not a link
                'flag_linkurl': False,
                'parent': 'register',
                'sortweight': 8.0,
                }),
            NavNode('register_deferred_finalize', {
                'menulabel': 'complete registration',
                'visible': lambda navnode,context: navnode.isactive(context),
                'flag_linkurl': False,
                'parent': 'register',
                'sortweight': 1.0,
                }),
            #
            NavNode('profile', {
                'menulabel': "profile",
                'menulabel_short': 'profile',
                'menuhint' : 'your profile',
                'visible': lambda navnode,context: context.get_value('user').get_isloggedin(),
                'parent': 'site',
                'sortweight': 7.0,
                'pagetitle': 'User Profile',
                }),
            #
            NavNode('userfield_verify', {
                'menulabel': "Verify user field",
                'visible': lambda navnode,context: navnode.isactive(context),
                'flag_linkurl': False,
                'parent': 'profile',
                'pagetitle': 'Verify User Field',
                }),
            #
            NavNode('resend_register_verification', {
                'menulabel': "Resend registration verification",
                'visible': lambda navnode,context: navnode.isactive(context),
                'flag_linkurl': False,
                'parent': 'register',
                }),
            NavNode('send_reset_password', {
                'menulabel': "Request password reset",
                'visible': lambda navnode,context: navnode.isactive(context),
                'flag_linkurl': False,
                'parent': 'profile',
                }),
            NavNode('reset_password', {
                'menulabel': "Perform password reset",
                'visible': lambda navnode,context: navnode.isactive(context),
                'flag_linkurl': False,
                'parent': 'profile',
                }),
            NavNode('modify_field', {
                'menulabel': "Change account profile field",
                'visible': lambda navnode,context: navnode.isactive(context),
                'flag_linkurl': False,
                'parent': 'profile',
                }),
            NavNode('login_bycode', {
                'menulabel': "Login by code",
                'visible': lambda navnode,context: navnode.isactive(context),
                'flag_linkurl': False,
                'parent': 'profile',
                }),
            ]

        # add nodes to site
        self.mewlosite.comp('navnodemanager').add_nodes(nodes)



