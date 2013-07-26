# testsite1.py
# This class defines a test site (and will run a debug test of it if started as main script)


# Mewlo imports
from mewlo.mpackages.core.msites import MewloSite

# Import the "mpackages" import which is just a subdirectory where the extensions specific to the site live; this is just a way to get the relative directory easily
import mpackages as sitempackageimport



















# the test1 demo site class
class MewloSite_Test1(MewloSite):

    def __init__(self):
        # call parent class init
        super(MewloSite_Test1, self).__init__()








    def add_settings_early(self):
        config = {}
        # site-specific extension home directory for this site (directory specified as a package, see top of file; could also be specified as absolute directory path string)
        config["sitepackageimport"] = [sitempackageimport]
        # site prefix?
        config["urlprefix"] = ""
        # add to settings
        self.sitesettings.merge_settings_atsection("config",config)



    def add_routes(self):
        # url routes (note that call properties must be dotted path to a function taking one argument (request)

        # add some urls
        self.routemanager.add_route( {
            "id": "homepage",
            "url": "/",
            "call": "request_home",
            } )
        self.routemanager.add_route( {
            "id": "aboutpage",
            "url": "/help/about",
            "call": "request_about",
            } )
        self.routemanager.add_route( {
            "id": "hellopage",
            "url": "/test/hello",
            "args": {
                    "id": "name",
                    "type": "string",
                    "required": True,
                    "help": "name of person to say hello to"
                    },
            "call": "request_sayhello",
            } )


























# if this python file is run as a script:

def main():

    # create a simple site from our test class and a sitemanager that supervises it
    sitemanager = MewloSite_Test1.create_manager_and_simplesite()

    # now ask the manager to debug and print some useful info
    print sitemanager.debug()

    # some simple tests
    print sitemanager.test_submit_url("/help/about")
    print sitemanager.test_submit_url("/test/hello/name/jesse")

    # start serving from web server test
    sitemanager.create_and_start_webserver_wsgiref()


if __name__ == "__main__":
    main()


