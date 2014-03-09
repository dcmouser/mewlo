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
from mewlo.mpacks.core.constants.mconstants import MewloConstants as mconst

# python imports
import os, sys

# our imports
import msiteaddon_account_manager

# this is just a way to get the relative directory easily, and we use this in config settings
import controllers as pkgdirimp_controllers







class MewloSiteAddon_Account(msiteaddon.MewloSiteAddon):
    """
    The MewloSiteAddon_Account class adds routes, controllers, and views related to logging in, registering, etc.
    """



    def __init__(self, mewlosite, debugmode):
        # call parent constructor
        super(MewloSiteAddon_Account, self).__init__(mewlosite, debugmode)
        # path prefix (used below in route setup)
        self.routepathprefix = '/account'
        # create the helper manager
        self.accountmanager = self.mewlosite.createappendcomp('accountmanager', msiteaddon_account_manager.AccountAddonManager)


    def prestartup_register(self, eventlist):
        """
        This is called for all managers, before any managers get startup() called.
        By the time this gets called you can be sure that ALL managers/components have been added to the site.
        The most important thing is that in this function managers create and register any database classes BEFORE they may be used in startup.
        The logic is that all managers must register their database classes, then the database tables will be build, then we can proceed to startup.
        """
        super(MewloSiteAddon_Account, self).prestartup_register(eventlist)


    def startup(self, eventlist):
        """
        Do preparatory stuff.
        """
        super(MewloSiteAddon_Account, self).startup(eventlist)


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
        self.mewlosite.settings.merge_settings_key(mconst.DEF_SETTINGSEC_aliases, aliases)




    def add_routes(self):
        """This is called by default by the base MewloSite near startup, to add routes to the system."""

        # create a routegroup
        routegroup = MewloRouteGroup()
        # overide the parent import-pack-directory for the urls in this group? if we don't it will use the controller root set in SITE config
        routegroup.set_controllerroot(pkgdirimp_controllers)
        routegroup.set_pathprefix(self.routepathprefix)

        routegroup.append(
            MewloRoute(
                id = 'login',
                path = '/login',
                controller = MewloController(root=pkgdirimp_controllers, function=self.accountmanager.request_login),
            ))
        routegroup.append(
            MewloRoute(
                id = 'logout',
                path = '/logout',
                controller = MewloController(root=pkgdirimp_controllers, function=self.accountmanager.request_logout),
            ))
        #
        routegroup.append(
            MewloRoute(
                id = 'register',
                path = '/register',
                controller = MewloController(root=pkgdirimp_controllers, function=self.accountmanager.request_register),
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
                controller = MewloController(root=pkgdirimp_controllers, function=self.accountmanager.request_register_deferred_verify),
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
                controller = MewloController(root=pkgdirimp_controllers, function=self.accountmanager.request_profile),
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
                controller = MewloController(root=pkgdirimp_controllers, function=self.accountmanager.request_userfield_verify),
            ))
        #
        routegroup.append(
            MewloRoute(
                id = 'resend_register_verification',
                path = '/resendverify',
                controller = MewloController(root=pkgdirimp_controllers, function=self.accountmanager.request_resend_register_verification),
            ))
        #
        routegroup.append(
            MewloRoute(
                id = 'send_reset_password',
                path = '/reqresetpassword',
                controller = MewloController(root=pkgdirimp_controllers, function=self.accountmanager.request_send_reset_password),
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
                controller = MewloController(root=pkgdirimp_controllers, function=self.accountmanager.request_reset_password),
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
                controller = MewloController(root=pkgdirimp_controllers, function=self.accountmanager.request_modify_field),
            ))
        routegroup.append(
            MewloRoute(
                id = 'cancel_modify_field',
                path = '/cancelmodify',
                args = [
                    MewloRouteArgString(
                        id = 'field',
                        required = True,
                        help = "field name whose verification to cancel",
                        ),
                    ],
                controller = MewloController(root=pkgdirimp_controllers, function=self.accountmanager.request_cancel_modify_field),
            ))


        # add routegroup we just created to the site
        self.mewlosite.comp('routemanager').append(routegroup)






    def add_navnodes(self):
        """Create navigational structure for site pages."""

        # these are related to Routes above, except that NavNodes are like a hierarchical menu structure / site map, wheras Routes are flat patterns that map to controllers
        nodes = [
            NavNode('login', {
                'visible': lambda navnode,context: not (context.get_value('clientuser').get_isloggedin()),
                'parent': 'site',
                'sortweight': 8.0,
                }),
            NavNode('logout', {
                'menulabel': lambda navnode,context: "logout ({0})".format(context.get_value('clientuser').get_username()),
                'menulabel_short': 'logout',
                'menuhint' : 'logout of your account',
                'visible': lambda navnode,context: context.get_value('clientuser').get_isloggedin(),
                'hide_evenifactive': True,
                'parent': 'site',
                'sortweight': 8.0,
                'pagetitle': 'Logout Page',
                }),
            #
            NavNode('register', {
                'visible': lambda navnode,context: not (context.get_value('clientuser').get_isloggedin()),
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
                'visible': lambda navnode,context: context.get_value('clientuser').get_isloggedin(),
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
                'menulabel': "Resend verification",
                'visible': lambda navnode,context: not context.get_value('clientuser').get_isloggedin(),
                #'flag_linkurl': False,
                'parent': 'site',
                'sortweight': 9.0,
                }),
            NavNode('resend_register_verification2', {
                'route': 'resend_register_verification',
                'menulabel': "Resend verification",
                'visible': lambda navnode,context: context.get_value('clientuser').get_isloggedin() and (navnode.isactive(context) or context.get_value('clientuser').get_ispending_newuser_verification()),
                #'flag_linkurl': False,
                'parent': 'profile',
                'sortweight': 9.0,
                }),

            NavNode('send_reset_password', {
                'menulabel': "Reset password",
                'visible': lambda navnode,context: not context.get_value('clientuser').get_isloggedin(),
                #'flag_linkurl': False,
                'parent': 'site',
                'sortweight': 9.0,
                }),
            NavNode('reset_password', {
                'menulabel': "Perform password reset",
                'visible': lambda navnode,context: navnode.isactive(context),
                'flag_linkurl': False,
                'parent': 'profile',
                }),
            NavNode('modify_field', {
                'menulabel': "Change account profile field",
                'visible': lambda navnode,context: context.get_value('clientuser').get_isloggedin(),
                #'flag_linkurl': False,
                'parent': 'profile',
                'urlargs': {'field':'email'},
                }),
            NavNode('cancel_modify_field', {
                'menulabel': "Cancel pending profile change",
                'visible': lambda navnode,context: navnode.isactive(context) or context.get_value('clientuser').get_ispending_fieldmodify_verification(context.get_value('request')),
                #'flag_linkurl': False,
                'parent': 'profile',
                'urlargs': {'field':'email'},
                }),
            ]

        # add nodes to site
        self.mewlosite.comp('navnodemanager').add_nodes(nodes)
















