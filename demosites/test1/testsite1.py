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








    def get_settings_config(self):
        # generic config
        config = {}
        # site-specific extension home directory for this site (directory specified as a package, see top of file; could also be specified as absolute directory path string)
        config["sitepackageimport"] = [sitempackageimport]
        # site prefix?
        config["urlprefix"] = ""
        #
        return config




    def get_settings_urls(self):
        # url routes (note that call properties must be dotted path to a function taking one argument (request)
        urls = []
        # add some urls
        urls.append( {
            "id": "homepage",
            "url": "/",
            "call": "request_home",
            } )
        urls.append( {
            "id": "aboutpage",
            "url": "/help/about",
            "call": "request_about",
            } )
        urls.append( {
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
        #
        return urls


























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


