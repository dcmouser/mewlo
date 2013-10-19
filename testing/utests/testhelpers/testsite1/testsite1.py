"""
testsite1.py
This class defines a test site (and will run a debug test of it if started as main script)
"""



# Mewlo imports
from mewlo.mpackages.core.site.msitemanager import MewloSiteManager
from mewlo.mpackages.core.site.msite import MewloSite
from mewlo.mpackages.core.controller.mcontroller import MewloController
from mewlo.mpackages.core.route.mroute import *
from mewlo.mpackages.core.navnode.mnav import NavNode, NavLink
from mewlo.mpackages.core.database import mdbmodel_log
from mewlo.mpackages.core.eventlog.mlogtarget_database import MewloLogTarget_Database
from mewlo.mpackages.core.setting.msettings import MewloSettings
from mewlo.mpackages.core.eventlog.mlogger import MewloLogger
from mewlo.mpackages.core.eventlog.mlogtarget_file import MewloLogTarget_File
from mewlo.mpackages.core.eventlog.mlogtarget_python import MewloLogTarget_Python
from mewlo.mpackages.core.eventlog.mevent import EWarning

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
        """This is called by default by the base MewloSite as the first thing to do at startup; here we expect to set some site settings that might be used during startup."""

        # config settings
        config = {
            # we set some package-directory-imports which will be the ROOT from which dynamic imports are done
            MewloSettings.DEF_SETTINGNAME_pkgdirimps_sitempackages: [pkgdirimp_sitempackages],
            MewloSettings.DEF_SETTINGNAME_controllerroot: pkgdirimp_controllers,
            MewloSettings.DEF_SETTINGNAME_sitefilepath: os.path.dirname(os.path.realpath(__file__)),
            MewloSettings.DEF_SETTINGNAME_siteurl_relative: '/mewlo',
            MewloSettings.DEF_SETTINGNAME_siteurl_absolute: 'http://127.0.0.1/mewlo',
            }
        self.settings.merge_settings_key(MewloSettings.DEF_SECTION_config, config)

        # extension package config
        packageconfig = {
            'mouser.mewlotestplug' : {
                'enabled': True,
                },
            'mouser.testpackage' : {
                'enabled': True,
                }
            }
        self.settings.merge_settings_key(MewloSettings.DEF_SECTION_packages, packageconfig)

        # database config
        databaseconfig = {
            'settings' : {
                'sqlalchemy_loglevel' : logging.NOTSET,
                },
            'default' : {
                'url' : 'sqlite:///${dbfilepath}/mewlo_testsite1.sqlite',
                'table_prefix': 'mewlo_',
                'flag_echologging' : False,
                },
            'mstry' : {
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
                id = "homepage",
                path = "/",
                controller = MewloController(function='requests.request_home')
                ))

        routegroup.append(
            MewloRoute(
                id = 'aboutpage',
                path = '/help/about',
                # we can pass the root package to the MewloController constructor, which has the benefit of doing the import immediately and raising exception if not found; otherwise the error will come up during preparation
                controller = MewloController(root=pkgdirimp_controllers, function='requests.request_about'),
                ))

        routegroup.append(
            MewloRoute(
                id = 'hellopage',
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




        #from controllers.requests import request_article
        routegroup.append(
            MewloRoute(
                id  = 'articlepage',
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
                controller = MewloController(function=pkgdirimp_controllers.requests.request_article),
                ))

        # add routegroup we just created to the site
        self.routes.append(routegroup)





    def add_navnodes(self):
        """Create navigational structure for site pages."""

        # create some test NavNodes
        nodes = [
            NavNode('home', {
                'title': 'The ${sitename} home page',
                'children': ['about','register','login','logout'],
                'route': 'homepage',
                }),
            NavNode('about', {
                'route': 'aboutpage',
                }),
            NavNode('register', {
                'visible': False,
                }),
            NavNode('login', {
                'visible': lambda pageinfo: not pageinfo.isloggedin,
                }),
            NavNode('logout', {
                'visible': lambda pageinfo: pageinfo.isloggedin,
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















def main():
    """This function is invoked by the python interpreter if this script itself is executed as the main script."""



    # commandline args
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--runserver", help="run the web server",action="store_true", default=False)
    parser.add_argument("-t", "--runtests", help="run some testsr",action="store_true", default=False)
    parser.add_argument("-d", "--debug", help="run in debug mode",action="store_true", default=False)
    args = parser.parse_args()
    #
    flag_debugsite = args.debug
    flag_runtests = args.runtests
    flag_runserver = args.runserver


    # Create a site manager and ask it to instantiate a site of the class we specify
    sitemanager = MewloSiteManager(flag_debugsite, MewloSite_Test1)

    # startup sites - this will generate any preparation errors
    sitemanager.startup()

    # check if there were any errors encountered during preparation of the s
    if (sitemanager.prepeventlist.count_errors() > 0):
        print "Stopping due to sitemanager preparation errors:"
        print sitemanager.prepeventlist.dumps()
        sys.exit(0)


    # start by displaying some debug info
    if (flag_debugsite):
        print sitemanager.dumps()




    # run tests?
    if (flag_runtests):
        # simulate some simple requests
        print sitemanager.test_submit_path('/')
        print sitemanager.test_submit_path('/help/about')
        print sitemanager.test_submit_path('/page/mystery')
        print sitemanager.test_submit_path('/test/hello/name/jesse/age/44')
        print sitemanager.test_submit_path('/test/hellot/name/jesse/age/44')

    # start serving the web server and process all web requests
    if (flag_runserver):
        # now process web requests
        sitemanager.create_and_start_webserver_wsgiref()

    # shutdown sites - we do this before exiting
    sitemanager.shutdown()


if __name__ == '__main__':
    main()


