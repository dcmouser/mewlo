# msites.py
# This file contains classes to handle Mewlo sites and site manager.


# global constants
DefMewlo_BasePackage_subdirlist = ["mpackages"]





# Import the mewlo modules we need from the mpackages/core directory
import mewlo
from msettings import MewloSettings
from mpackage import MewloPackageManager
from mrequest import MewloRequest
from mresponse import MewloResponse
from mroutemanager import MewloRouteManager


# python libs
import os
from datetime import datetime, date, time










class MewloSite(object):
    """
    The MewloSite class represents a single "site" that handles requests.
    Typically you will only have one site running.
    """

    def __init__(self):
        # initialize settings
        self.sitemanager = None
        # create site settings
        self.sitesettings = MewloSettings()
        # collection of mewlo addon packages
        self.packagemanager = MewloPackageManager(self)
        # route manager
        self.routemanager = MewloRouteManager(self)


    def merge_settings(self, in_settings):
        # merge in some settings
        self.sitesettings.merge_settings(in_settings)


    def create_and_prepare_standalone_sitemanager(self):
        """Create and prepare a single-site sitemananger specifically for this site"""
        # create site manager
        mysitemanager = MewloSiteManager()
        # set it to be our site manager
        self.set_and_add_sitemanager(mysitemanager)
        # ask it to prepare for work
        self.sitemanager.prepare()
        # return the site manager created
        return self.sitemanager


    def set_and_add_sitemanager(self, in_sitemanager):
        # initialize settings
        self.sitemanager = in_sitemanager
        # register the site with the site manager
        self.sitemanager.add_site(self)




    def get_package_directory_list(self):
        """Return a list of absolute directory paths where (addon) packages should be scanned"""
        packagedirectories = []
        sitepackages = self.sitesettings.get_sectionvalue("config","sitempackageimport")
        if (sitepackages==None):
            pass
        else:
            for sitepackage in sitepackages:
                if (isinstance(sitepackage, basestring)):
                    # it's a string, use it directly
                    packagepath = sitepackage
                else:
                    # it's a module import, get it's directory
                    packagepath = os.path.dirname(os.path.realpath(sitepackage.__file__))
                # add path string to our list
                packagedirectories.append(packagepath)
        #
        return packagedirectories


    def prepare(self):
        """Do stuff after settings have been set """
        self.discover_packages()
        self.loadinfos_packages()
        self.instantiate_packages()

    def discover_packages(self):
        """Discover packages """
        packagedirectories = self.sitemanager.get_package_directory_list() + self.get_package_directory_list()
        self.packagemanager.set_directories(packagedirectories)
        self.packagemanager.discover_packages()

    def loadinfos_packages(self):
        """Load infos for all packages """
        self.packagemanager.loadinfos_packages()

    def instantiate_packages(self):
        """load and instantiate packages"""
        self.packagemanager.instantiate_packages()





    def setup_early(self):
        self.add_settings_early()
        self.add_routes()

    def add_settings_early(self):
        pass

    def add_routes(self):
        pass








    def process_request(self, request):
        # return True if the request is for this site and we have set request.response
        ishandled = self.routemanager.process_request(request)
        return ishandled









    @classmethod
    def create_manager_and_simplesite(cls):
        """This is a convenience helper function to aid in testing of MewloSite derived classes."""
        # create instance of site -- we do it this way so it will create the DERIVED class
        mysite = cls()
        # we need to apply our early settings
        mysite.setup_early()
        # now create a manager using just this site
        sitemanager = mysite.create_and_prepare_standalone_sitemanager()
        # now return the manager
        return sitemanager





    def debug(self,indentstr=""):
        outstr = indentstr+"MewloSite (" + self.__class__.__name__ +") reporting in.\n"
        outstr += self.sitesettings.debug(indentstr+" ")
        outstr += self.packagemanager.debug(indentstr+" ")
        outstr += self.routemanager.debug(indentstr+" ")
        return outstr













class MewloSiteManager(object):
    """
    The MewloManager class holds a collection of Mewlo "sites", which can handle incoming requests.
    Typically, you would have only one single site running from your web server, but there may be times when you want to server multiple sites from a single instantiation running off a single port.
    When supporting multiple sites, the sites are completely independent of one another, and must have completely separate uri prefixes.  They share nothing.
    """

    def __init__(self):
        # the collection of sites that this manager takes care of
        self.sites = list()


    def add_site(self,site):
        self.sites.append(site)


    def get_installdir(self):
        path = os.path.dirname(os.path.realpath(mewlo.__file__))
        return path

    def get_package_directory_list(self):
        """Return a list of directories in the base/install path of Mewlo, where addon packages should be scanned"""
        basedir = self.get_installdir()
        packagedirectories = [basedir+"/"+dir for dir in DefMewlo_BasePackage_subdirlist]
        return packagedirectories


    def prepare(self):
        """Ask sites to load all enabled packages"""
        for site in self.sites:
            site.prepare()


    def log(self, str):
        nowtime = datetime.now()
        outstr = "MEWLODEBUG ["+nowtime.strftime("%B %d, %Y at %I:%M%p")+"]: "+str
        print outstr





    def test_submit_path(self, pathstr):
        """Simulate the submission of a url"""
        outstr = ""
        outstr += "Testing submission of url: "+pathstr+"\n"
        # generate request and debug it
        request = MewloRequest.createrequest_from_pathstring(self,pathstr)
        outstr += request.debug()
        # generate response and debug it
        self.process_request(request)
        outstr += request.response.debug()
        # return debug text
        return outstr










    def create_and_start_webserver_wsgiref(self, portnumber=8080):
        """Create a wsgiref web server and begin serving requests."""
        # see http://lucumr.pocoo.org/2007/5/21/getting-started-with-wsgi/
        from wsgiref.simple_server import make_server
        srv = make_server('localhost', portnumber, self.wsgiref_callback)
        srv.serve_forever()





















    def process_request(self, request):
        # first do any pre-processing on the request
        self.preprocess_request(request)
        # walk through the site list and let each site take a chance at processing the request
        for site in self.sites:
            ishandled = site.process_request(request)
            if (ishandled):
                # ok this site handled it
                break

        if (not ishandled):
            # no site handled it, so this is an error
            request.response.add_status_error(404,"Page not found or supported on any site: '"+request.get_path()+"'")

        # return response
        return True



    def wsgiref_callback(self, environ, start_response):
        """Receive a callback from wsgi web server"""
        outstr = "wsgiref_callback:\n"
        outstr += " "+str(environ)+"\n"
        outstr += " "+str(start_response)+"\n"
        self.log(outstr)
        # create request
        request = MewloRequest.createrequest_from_wsgiref_environ(self, environ)
        # get response
        ishandled = self.process_request(request)
        # process response
        return request.response.start_and_make_wsgiref_response(start_response)



    def preprocess_request(self, request):
        # pre-process and parse the request
        request.preprocess()



















    def debug(self,indentstr=''):
        outstr = indentstr+"MewloSiteManager reporting in.\n"
        outstr += self.debug_sites(indentstr+" ")
        return outstr

    def debug_sites(self,indentstr=" "):
        outstr = indentstr+"Sites:\n"
        indentstr+=" "
        if (len(self.sites)==0):
            outstr += indentstr+"None.\n"
        for site in self.sites:
            outstr += site.debug(indentstr+" ")+"\n"
        return outstr















