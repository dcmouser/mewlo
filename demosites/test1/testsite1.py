# testsite1.py
# This class defines a test site (and will run a debug test of it if started as main script)


# Mewlo imports
from mewlo.mpackages.core.msites import MewloSite
from mewlo.mpackages.core.mroutemanager import *
from mewlo.mpackages.core.mcontroller import MewloController

# helpers
#from mewlo.mpackages.core.helpers.callables import findcallable

# Import the "mpackages" import which is just a subdirectory where the extensions specific to the site live; this is just a way to get the relative directory easily
import mpackages as pkgdirimp_sitempackages
import controllers as pkgdirimp_controllers















# the test1 demo site class
class MewloSite_Test1(MewloSite):

    def __init__(self):
        # call parent class init
        super(MewloSite_Test1, self).__init__(__name__)







    def add_settings_early(self):
        config = {
            # we set some package-directory-imports which will be the ROOT from which dynamic imports are done
            MewloSite.DEF_CONFIGVAR_pkgdirimps_sitempackages: [pkgdirimp_sitempackages],
            MewloSite.DEF_CONFIGVAR_controllerroot: pkgdirimp_controllers,
            # site prefix
            MewloSite.DEF_CONFIGVAR_urlprefix: "",
            }
        # add config to settings
        self.sitesettings.merge_settings_atsection("config",config)



    def add_routes(self):
        # url routes (note that call properties must be dotted path to a function taking one argument (request)

        # create a routegroup
        routegroup = MewloRouteGroup()
        # overide the parent import-package-directory for the urls in this group? if we don't it will use the controller root set in SITE config
        # routegroup.set_controllerroot(pkgdirimp_controllers)
        # another way to specify controller functions directly
        from controllers.requests import request_article
        #
        routegroup.append(
            MewloRoute(
                id = "homepage",
                path = "/",
                controller = MewloController(function="requests.request_home")
                ))

        routegroup.append(
            MewloRoute(
                id = "aboutpage",
                path = "/help/about",
                # we can pass the root package to the MewloController constructor, which has the benefit of doing the import immediately and raising exception if not found; otherwise the error will come up during preparation
                controller = MewloController(root=pkgdirimp_controllers, function="requests.request_about"),
                ))

        routegroup.append(
            MewloRoute(
                id = "hellopage",
                path = "/test/hello",
                args = [
                        MewloRouteArgString(
                            id = "name",
                            required = True,
                            help = "name of person to say hello to",
                            ),
                        MewloRouteArgInteger(
                            id = "age",
                            required = False,
                            help = "age of person (optional)",
                            )
                        ],
                controller = MewloController(function="requests.request_sayhello"),
                extra = [ "whatever we want" ],
                ))

        routegroup.append(
            MewloRoute(
                id  = "articlepage",
                path = "/article",
                args = [
                        MewloRouteArgString(
                            id = "title",
                            required = False,
                            positional = True,
                            help = "title of article to display",
                            )
                        ],
#                controller = MewloController(function="requests.request_article"),
                # another alternative is to import above and then specify the function reference explicitly
                controller = MewloController(function=request_article),
                ))
        #
        # add routegroup to site
        self.routes.append(routegroup)
























# if this python file is run as a script:

def main():

    # create a simple site from our test class and a sitemanager that supervises it
    sitemanager = MewloSite_Test1.create_manager_and_simplesite()

    # stop if there were errors preparing
    if (sitemanager.prepare_errors.counterrors()>0):
        print "Stopping due to sitemanager preparation errors:\n"
        print sitemanager.prepare_errors.debug()
        exit()


    # ask the manager to debug and print some useful info
    print sitemanager.debug()


    # some simple tests
    print sitemanager.test_submit_path("/help/about")
    print sitemanager.test_submit_path("/page/mystery")
    print sitemanager.test_submit_path("/test/hello/name/jesse/age/44")

    # start serving from web server test
    sitemanager.create_and_start_webserver_wsgiref()


if __name__ == "__main__":
    main()


