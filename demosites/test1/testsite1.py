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
        config = {
            # site-specific extension home directory for this site (directory specified as a package, see top of file; could also be specified as absolute directory path string)
            "sitepackageimport": [sitempackageimport],
            # site prefix
            "urlprefix": "",
            }
        # add to settings
        self.sitesettings.merge_settings_atsection("config",config)



    def add_routes(self):
        # url routes (note that call properties must be dotted path to a function taking one argument (request)

        # add some urls
        self.routemanager.add_route( {
            "id": "homepage",
            "path": "/",
            "allow_extra_args": False,
            "call": "request_home",
            } )
        self.routemanager.add_route( {
            "id": "aboutpage",
            "path": "/help/about",
            "allow_extra_args": False,
            "call": "request_about",
            } )
        self.routemanager.add_route( {
            "id": "hellopage",
            "path": "/test/hello",
            "args": [
                        {
                        "id": "name",
                        "type": "STRING",
                        "required": True,
                        "help": "name of person to say hello to",
                        },
                        {
                        "id": "age",
                        "type": "INTEGER",
                        "required": False,
                        "help": "age of person to say hello to",
                        },
                    ],
            "allow_extra_args": False,
            "call": "request_sayhello",
            } )


























# if this python file is run as a script:

def main():

    # create a simple site from our test class and a sitemanager that supervises it
    sitemanager = MewloSite_Test1.create_manager_and_simplesite()

    # now ask the manager to debug and print some useful info
    print sitemanager.debug()

    # some simple tests
    print sitemanager.test_submit_path("/help/about")
    print sitemanager.test_submit_path("/test/hello/name/jesse/age/44")

    # start serving from web server test
    sitemanager.create_and_start_webserver_wsgiref()


if __name__ == "__main__":
    main()


