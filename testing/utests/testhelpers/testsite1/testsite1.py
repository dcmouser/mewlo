"""
testsite1.py
This class defines a test site (and will run a debug test of it if started as main script)
"""



# Mewlo imports
from mewlo.mpackages.core.site.msitemanager import MewloSiteManager
from mewlo.mpackages.core.site.msite import MewloSite
from mewlo.mpackages.core.controller.mcontroller import MewloController
from mewlo.mpackages.core.controller.mcontroller_staticfiles import MewloController_StaticFiles
from mewlo.mpackages.core.route.mroute import *
from mewlo.mpackages.core.route.mroute_staticfiles import MewloRoute_StaticFiles
from mewlo.mpackages.core.navnode.mnav import NavNode, NavLink
from mewlo.mpackages.core.database import mdbmodel_log
from mewlo.mpackages.core.eventlog.mlogtarget_database import MewloLogTarget_Database
from mewlo.mpackages.core.setting.msettings import MewloSettings
from mewlo.mpackages.core.eventlog.mlogger import MewloLogger
from mewlo.mpackages.core.eventlog.mlogtarget_file import MewloLogTarget_File
from mewlo.mpackages.core.eventlog.mlogtarget_python import MewloLogTarget_Python
from mewlo.mpackages.core.eventlog.mevent import EWarning
from mewlo.mpackages.core.rbac import mrbac



# Import the "mpackages" import which is just a subdirectory where the extensions specific to the site live;
# this is just a way to get the relative directory easily, and we use this in config settings
import mpackages as pkgdirimp_sitempackages
import controllers as pkgdirimp_controllers

# python imports
import os, sys
import logging



# the test1 demo site class
class MewloSite_Test1(MewloSite):

    def __init__(self, debugmode):
        # call parent constructor
        super(MewloSite_Test1, self).__init__(__name__, debugmode)



    def add_settings_early(self):
        """This is called by default by the base MewloSite as the first thing to do at startup;
        here we expect to set some site settings that might be used during startup."""


        # config settings
        config = {
            # we set some package-directory-imports which will be the ROOT from which dynamic imports are done
            MewloSettings.DEF_SETTINGNAME_pkgdirimps_sitempackages: [pkgdirimp_sitempackages],
            MewloSettings.DEF_SETTINGNAME_flag_importsetuptoolspackages: True,
            MewloSettings.DEF_SETTINGNAME_controllerroot: pkgdirimp_controllers,
            MewloSettings.DEF_SETTINGNAME_sitefilepath: os.path.dirname(os.path.realpath(__file__)),
            }
        self.settings.merge_settings_key(MewloSettings.DEF_SECTION_config, config)

        # config settings
        config = {
            # these siteurls should not end in / so if you are serving a site at root just use relative of '' and absolute of 'http://sitename.com'
            MewloSettings.DEF_SETTINGNAME_siteurl_relative: '',
            MewloSettings.DEF_SETTINGNAME_siteurl_absolute: 'http://127.0.0.1:8080',
#            MewloSettings.DEF_SETTINGNAME_siteurl_relative: '/public/publicity',
#            MewloSettings.DEF_SETTINGNAME_siteurl_absolute: 'http://127.0.0.1:8080/public/publicity',
            MewloSettings.DEF_SETTINGNAME_sitename: 'Mewlo',
            }
        self.settings.merge_settings_key(MewloSettings.DEF_SECTION_config, config)

        # config settings
        config = {
            MewloSettings.DEF_SETTINGNAME_isenabled: True,
            MewloSettings.DEF_SETTINGNAME_isonline: True,
            MewloSettings.DEF_SETTINGNAME_offline_mode: 'maintenance',
            MewloSettings.DEF_SETTINGNAME_offline_message: 'We are down for leap-year maintenance; we will be back soon.',
            MewloSettings.DEF_SETTINGNAME_offline_allowadmin: False,
            }
        self.settings.merge_settings_key(MewloSettings.DEF_SECTION_config, config)



        # extension package config
        packageconfig = {
            'mouser.mewlotestplug' : {
                'enabled': True,
                },
            'mouser.testpackage' : {
                'enabled': True,
                },
            }
        self.settings.merge_settings_key(MewloSettings.DEF_SECTION_packages, packageconfig)

        # database config
        databaseconfig = {
            'settings' : {
                'sqlalchemy_loglevel' : logging.NOTSET,
                #'sqlalchemy_loglevel' : logging.INFO,
                },
            'default' : {
                'url' : 'sqlite:///${dbfilepath}/mewlo_testsite1.sqlite',
                'table_prefix': 'mewlo_',
                'flag_echologging' : False,
                },
            'mysql_unused' : {
                # Sample configuration for mysql
                'url' : 'mysql://mewlo_user:mewlo_pass@localhost:3306/mewlo_testsite1',
                'table_prefix': 'mewlo_'
                },
            }
        self.settings.merge_settings_key(MewloSettings.DEF_SECTION_database, databaseconfig)










    def add_loggers(self):
        """This is called by default by the base MewloSite near startup, to add loggers to the system."""

        # create a single logger (with no filters); multiple loggers are supported because each logger can have filters that define what this logger filters out
        logger = self.add_logger(MewloLogger('mytestlogger'))

        # now add some targets (handlers) to it
        logger.add_target(MewloLogTarget_File(filename=self.resolve('${logfilepath}/testlogout1.txt'), filemode='w'))

        if (False):
            # want to test raising an exception on failure to write/open file? uncomment this
            logger.add_target(MewloLogTarget_File(filename=''))

        if (True):
            # let's add standard python logging as a test, and route that to file
            import logging
            pythonlogger = MewloLogTarget_Python.make_simple_pythonlogger_tofile('mewlo', self.resolve('${logfilepath}/testlogout3.txt'))
            logger.add_target(MewloLogTarget_Python(pythonlogger))
            # and then as a test, let's create an error message in this log
            pythonlogger.error("This is a manual python test error.")

        if (True):
            # let's add a database logger
            logger.add_target(MewloLogTarget_Database(baseclass=mdbmodel_log.MewloDbModel_Log, tablename='log'))





    def add_routes(self):
        """This is called by default by the base MewloSite near startup, to add routes to the system."""

        # create a routegroup
        routegroup = MewloRouteGroup()
        # overide the parent import-package-directory for the urls in this group? if we don't it will use the controller root set in SITE config
        # routegroup.set_controllerroot(pkgdirimp_controllers)

        routegroup.append(
            MewloRoute(
                id = 'home',
                path = "/",
                controller = MewloController(function='requests.request_home')
                ))


        routegroup.append(
            MewloRoute(
                id = 'hello',
                path = '/test/hello',
                args = [
                        MewloRouteArgString(
                            id = 'name',
                            required = True,
                            help = "name of person to say hello to",
                            ),
                        MewloRouteArgInteger(
                            id = 'age',
                            required = False,
                            help = "age of person (optional)",
                            defaultval = 44,
                            )
                        ],
                controller = MewloController(function="requests.request_sayhello"),
                # we can pass in any extra data which will just be part of the route that can be examined post-matching
                extras = { 'stuff': "whatever we want" },
                # we can force the route to simulate as if certain url call args were assigned (this works whether there are RouteArgs for these or not; no type checking is performed on them)
                forcedargs = { 'sign': u"aries" },
                ))



        from controllers import requests
        routegroup.append(
            MewloRoute(
                id  = 'article',
                path = '/article',
                args = [
                        MewloRouteArgString(
                            id = 'title',
                            required = False,
                            positional = True,
                            help = "title of article to display",
                            )
                        ],
                # another way to specify the controller is to pass in the actual function reference (rather than as a string)
                controller = MewloController(function=requests.request_article),
                ))

        routegroup.append(
            MewloRoute(
                id = 'help',
                path = '/user/help',
                controller = MewloController(root=pkgdirimp_controllers, function='requests.request_help'),
                ))
        routegroup.append(
            MewloRoute(
                id = 'contact',
                path = '/help/contact',
                # we can pass the root package to the MewloController constructor, which has the benefit of doing the import immediately and raising exception if not found; otherwise the error will come up during preparation
                controller = MewloController(root=pkgdirimp_controllers, function='requests.request_contact'),
                ))
        routegroup.append(
            MewloRoute(
                id = 'about',
                path = '/help/about',
                # we can pass the root package to the MewloController constructor, which has the benefit of doing the import immediately and raising exception if not found; otherwise the error will come up during preparation
                controller = MewloController(root=pkgdirimp_controllers, function='requests.request_about'),
                ))

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


        #static file server
        routegroup.append(
            MewloRoute_StaticFiles(
                id  = 'static_files',
                path = '/static',
                controller = MewloController_StaticFiles(
                    sourcepath = '${sitefilepath}/public_html'
                    ),
                ))





        # add routegroup we just created to the site
        self.routemanager.append(routegroup)









    def add_navnodes(self):
        """Create navigational structure for site pages."""

        # create some test NavNodes
        nodes = [
            NavNode('home', {
                'menulabel': '${sitename} home page',
                'menulabel_short': 'home',
                'children': [],
                'parent': 'site',
                'sortweight': 1.0,
                'menuhint' : 'Return to the home page'
                }),
            NavNode('help', {
                'parent': 'site',
                'sortweight': 10.0,
                }),
            NavNode('contact', {
                'parent': 'help',
                'sortweight': 8.0,
                }),
            NavNode('about', {
                'parent': 'help',
                'sortweight': 9.0,
                }),
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
        self.navnodes.add_nodes(nodes)





























    def pre_runroute_callable(self, route, request):
        """This is called by default when a route is about to be invoked.  Subclassed sites can override it."""
        request.logevent(EWarning("This is a test1 warning called PRE run route: " + request.get_path()))
        # ATTN: test, let's trigger a signale
        if (True):
            id = 'signal.site.pre_runroute'
            message = {'route':route}
            source = None
            flag_collectresults = True
            signalresults = self.dispatcher.broadcast(id, message, request, source, flag_collectresults)
        return None


    def post_runroute_callable(self, request):
        """This is called by default after a route has been invoked.  Subclassed sites can override it."""
        request.logevent(EWarning("This is a test2 warning called POST run route: " + request.get_path(), flag_loc=True))
        return None





    @classmethod
    def runmodeltests(cls):
        """Some tests that we should move elsewhere eventually."""
        from mewlo.mpackages.core.user import muser
        from mewlo.mpackages.core.group import mgroup
        #
        usera = muser.MewloUser()
        userb = muser.MewloUser()
        groupa = mgroup.MewloGroup()
        groupb = mgroup.MewloGroup()

        # save users and groups
        usera.save()
        userb.save()
        groupa.save()
        groupb.save()

        # role test
        from mewlo.mpackages.core.rbac import mrbac
        rolea = mrbac.MewloRole()
        roleb = mrbac.MewloRole()
        rolea.save()
        roleb.save()
        rolea.childroles.append(roleb)
        rolea.save()


















def main():
    """This function is invoked by the python interpreter if this script itself is executed as the main script."""



    # commandline args
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", help="run in debug mode (combine with others)",action="store_true", default=False)
    parser.add_argument("-s", "--runserver", help="run the web server",action="store_true", default=False)
    parser.add_argument("-t", "--querytests", help="run some testsr",action="store_true", default=False)
    parser.add_argument("-m", "--modeltests", help="run some model tests",action="store_true", default=False)
    args = parser.parse_args()
    #
    flag_debugsite = args.debug
    flag_runtests_query = args.querytests
    flag_runtests_model = args.modeltests
    flag_runserver = args.runserver


    # Create a site manager and ask it to instantiate a site of the class we specify
    sitemanager = MewloSiteManager(flag_debugsite, MewloSite_Test1)

    # startup sites - this will generate any preparation errors
    sitemanager.startup()

    # check f there were any errors encountered during preparation of the s
    if (sitemanager.prepeventlist.count_errors() > 0):
        print "Stopping due to sitemanager preparation errors:"
        print sitemanager.prepeventlist.dumps()
        sys.exit(0)


    # start by displaying some debug info
    if (flag_debugsite):
        print "Debugging site manager."
        print sitemanager.dumps()


    if (flag_runtests_query):
        # simulate some simple simulated query requests
        print "Running query tests."
        print sitemanager.test_submit_path('/')
        print sitemanager.test_submit_path('/help/about')
        print sitemanager.test_submit_path('/page/mystery')
        print sitemanager.test_submit_path('/test/hello/name/jesse/age/44')

    if (flag_runtests_model):
        # run model tests
        print "Running model tests."
        MewloSite_Test1.runmodeltests()


    if (flag_runserver):
        # start serving the web server and process all web requests
        print "Starting web server."
        sitemanager.create_and_start_webserver_wsgiref()


    # shutdown sites - we do this before exiting
    print "Shutting down."
    sitemanager.shutdown()


if __name__ == '__main__':
    main()


