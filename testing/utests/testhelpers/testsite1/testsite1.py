"""
testsite1.py
This class defines a test site (and will run a debug test of it if started as main script)
"""



# Mewlo imports
from mewlo.mpacks.core.site.msitemanager import MewloSiteManager
from mewlo.mpacks.core.site.msite import MewloSite
from mewlo.mpacks.core.controller.mcontroller import MewloController
from mewlo.mpacks.core.controller.mcontroller_staticfiles import MewloController_StaticFiles
from mewlo.mpacks.core.route.mroute import *
from mewlo.mpacks.core.route.mroute_staticfiles import MewloRoute_StaticFiles
from mewlo.mpacks.core.navnode.mnav import NavNode, NavLink
from mewlo.mpacks.core.database import mdbmodel_log
from mewlo.mpacks.core.eventlog.mlogtarget_database import MewloLogTarget_Database
from mewlo.mpacks.core.setting.msettings import MewloSettings
from mewlo.mpacks.core.eventlog.mlogger import MewloLogger
from mewlo.mpacks.core.eventlog.mlogtarget_file import MewloLogTarget_File
from mewlo.mpacks.core.eventlog.mlogtarget_python import MewloLogTarget_Python
from mewlo.mpacks.core.eventlog.mevent import EWarning
from mewlo.mpacks.core.constants.mconstants import MewloConstants as mconst

# account addon
from mewlo.mpacks.site_addons.account import msiteaddon_account
#from mewlo.mpacks.site_addons.account import accountmanager


# python imports
import os, sys
import logging




# Import the "mpacks" import which is just a subdirectory where the extensions specific to the site live;
# this is just a way to get the relative directory easily, and we use this in config settings
import mpacks as pkgdirimp_sitempacks
import controllers as pkgdirimp_controllers
import config as pkgdirimp_config





# the test1 demo site class
class MewloSite_Test1(MewloSite):

    def __init__(self, debugmode, commandlineargs=None, defaultconfigname='mouser'):
        # first call parent constructor
        super(MewloSite_Test1, self).__init__(__name__, debugmode, commandlineargs, defaultconfigname)


    def get_pkgdirimp_config(self):
        # returns the package directory import where config settings files live
        # either if these will work -- we can return file path OR package
        if (True):
            return pkgdirimp_config
        else:
            return os.path.dirname(os.path.realpath(__file__))+'/config'


    def add_settings_early(self):
        """
        This is called by default by the base MewloSite as the first thing to do at startup;
        here we expect to set some site settings that might be used early during startup.
        """

        # config settings
        config = {
            # some generic settings for every site, to point to location of some stuff
            mconst.DEF_SETTINGNAME_pkgdirimps_sitempacks: [pkgdirimp_sitempacks],
            mconst.DEF_SETTINGNAME_controllerroot: pkgdirimp_controllers,
            mconst.DEF_SETTINGNAME_sitefilepath: os.path.dirname(os.path.realpath(__file__)),
            # should we also load mewlo site installed setuptools plugins
            mconst.DEF_SETTINGNAME_flag_importsetuptoolspacks: True,
            }
        self.settings.merge_settings_key(mconst.DEF_SETTINGSEC_config, config)

        # config settings
        config = {
            # Name of site
            mconst.DEF_SETTINGNAME_sitename: 'Mewlo',
            # Specify where this site serves from
            # these siteurls should not end in / so if you are serving a site at root just use relative of '' and absolute of 'http://sitename.com'
            mconst.DEF_SETTINGNAME_siteurl_relative: '',
            mconst.DEF_SETTINGNAME_siteurl_absolute: 'http://127.0.0.1:8080',
            #mconst.DEF_SETTINGNAME_siteurl_relative: '/public/publicity',
            #mconst.DEF_SETTINGNAME_siteurl_absolute: 'http://127.0.0.1:8080/public/publicity',
            }
        self.settings.merge_settings_key(mconst.DEF_SETTINGSEC_config, config)

        # config settings
        config = {
            # online status information
            mconst.DEF_SETTINGNAME_isenabled: True,
            mconst.DEF_SETTINGNAME_isonline: True,
            mconst.DEF_SETTINGNAME_offline_mode: 'maintenance',
            mconst.DEF_SETTINGNAME_offline_message: 'We are down for leap-year maintenance; we will be back soon.',
            mconst.DEF_SETTINGNAME_offline_allowadmin: False,
            }
        self.settings.merge_settings_key(mconst.DEF_SETTINGSEC_config, config)



        # config some aliases we can use (for example in our templates)
        aliases = {
            # let's add an alias to where we are going to serve static files from (note this is pointing not to a directory but to a ROUTE path)
            'staticurl': '${siteurl_relative}/static',
            }
        self.settings.merge_settings_key(mconst.DEF_SETTINGSEC_aliases, aliases)


        # extension pack config -- we need to explicitly enable plugins
        packconfig = {
            'mouser.mewlotestplug' : {
                'isenabled': True,
                },
            'mouser.testpack' : {
                'isenabled': True,
                },
            }
        self.settings.merge_settings_key(mconst.DEF_SETTINGSEC_packs, packconfig)


        # database config
        databaseconfig = {
            'settings' : {
                'sqlalchemy_loglevel' : logging.NOTSET,
                #'sqlalchemy_loglevel' : logging.INFO,
                },
            'default' : {
                'url' : 'sqlite:///${dbfilepath}/mewlo_testsite1.sqlite',
                #'tablename_prefix': 'mewlo_',
                'flag_echologging' : False,
                },
            'mysql_unused' : {
                # Sample configuration for mysql
                'url' : 'mysql://mewlo_user:mewlo_pass@localhost:3306/mewlo_testsite1',
                'tablename_prefix': 'mewlo_'
                },
            }
        self.settings.merge_settings_key(mconst.DEF_SETTINGSEC_database, databaseconfig)


        # email config settings
        mailconfig = {
            # online status information
            'smtp_host': self.get_configval('mail_smtp_host'),
            'smtp_login': self.get_configval('mail_smtp_login'),
            'smtp_port': self.get_configval('mail_smtp_port'),
            'smtp_mode': self.get_configval('mail_smtp_mode'),
            'smtp_password': self.get_configval('mail_smtp_password'),
            'mail_from' : self.get_configval('mail_from'),
            }
        self.settings.merge_settings_key(mconst.DEF_SETTINGSEC_mail, mailconfig)













    def add_loggers(self):
        """This is called by default by the base MewloSite near startup, to add loggers to the system."""

        # create a single logger (with no filters); multiple loggers are supported because each logger can have filters that define what this logger filters out
        logger = self.add_logger(MewloLogger('mytestlogger'))

        # now add some targets (handlers) to it
        logger.add_target(MewloLogTarget_File(filename=self.resolve('${logfilepath}/testlogout1.txt'), filemode='w'))

        if (False):
            # want to test raising an exception on failure to write/open file? uncomment this -- the bad blank filename will throw an exception
            logger.add_target(MewloLogTarget_File(filename=''))

        if (True):
            # let's add standard python logging as a test, and route that to file; this creates a standard python-style logger and catches events sent to that
            import logging
            pythonlogger = MewloLogTarget_Python.make_simple_pythonlogger_tofile('mewlo', self.resolve('${logfilepath}/testlogout_python.txt'))
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
        # overide the parent import-pack-directory for the urls in this group? if we don't it will use the controller root set in SITE config
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
                # we can pass the root pack to the MewloController constructor, which has the benefit of doing the import immediately and raising exception if not found; otherwise the error will come up during preparation
                controller = MewloController(root=pkgdirimp_controllers, function='requests.request_contact'),
                ))
        routegroup.append(
            MewloRoute(
                id = 'about',
                path = '/help/about',
                # we can pass the root pack to the MewloController constructor, which has the benefit of doing the import immediately and raising exception if not found; otherwise the error will come up during preparation
                controller = MewloController(root=pkgdirimp_controllers, function='requests.request_about'),
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
        self.comp('routemanager').append(routegroup)










    def add_navnodes(self):
        """Create navigational structure for site pages."""

        # these are related to Routes above, except that NavNodes are like a hierarchical menu structure / site map, wheras Routes are flat patterns that map to controllers
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
            ]

        # add nodes to site
        self.comp('navnodemanager').add_nodes(nodes)








    def add_addons(self):
        """Add any site addons."""
        # register accountmanager addon component
        self.createappendcomp('accountaddon', msiteaddon_account.MewloSiteAddon_Account)






























    def pre_runroute_callable(self, route, request):
        """This is called by default when a route is about to be invoked.  Subclassed sites can override it."""

        #request.logevent(EInfo("pre_runroute_callable Request URL: {0} from {1}.".format(request.get_full_path(), request.get_remote_addr())))
        # ATTN: test, let's trigger a signal
        if (False):
            id = 'signal.site.pre_runroute'
            message = {'route':route}
            source = None
            flag_collectresults = True
            signalresults = self.comp('signalmanager').broadcast(id, message, request, source, flag_collectresults)
        return None



    def post_runroute_callable(self, request):
        """This is called by default after a route has been invoked.  Subclassed sites can override it."""

        #request.logevent(EWarning("This is a test warning called POST run route: " + request.get_path()))
        return None
















































def main():
    """This function is invoked by the python interpreter if this script itself is executed as the main script."""

    # custom commandline args (if we dont have any we can pass None instead of parser to do_main_commandline_startyp()).
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--querytests", help="run some test queries",action="store_true", default=False)

    # Create a site manager and ask it to instantiate a site of the class we specify, and handle some generic commandline options
    # it returns parsed commandline args so we can look for any custom ones
    args, sitemanager = MewloSiteManager.do_main_commandline_startup(MewloSite_Test1, parser)

    # on successful creation, we can parse and do some stuff
    if (sitemanager != None):
        # sitemanager was created and early commandline processing done
        # now we have some custom commandline arg proessing we might want to do
        if (sitemanager.is_readytoserve()):
            # this stuff only is entertained if sitemanager says all green lights
            if (args.querytests):
                # simulate some simple simulated query requests
                print "Running query tests."
                print sitemanager.test_submit_path('/')
                print sitemanager.test_submit_path('/help/about')
                print sitemanager.test_submit_path('/page/mystery')
                print sitemanager.test_submit_path('/test/hello/name/jesse/age/44')

        # now any late generic commandline stuff (including serving the website)
        sitemanager.do_main_commandline_late()


if __name__ == '__main__':
    main()


