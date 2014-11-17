# utest1.py
# This is a unit test module for mewlo
#
# It uses the python unittest framework to manage test running and reporting


# mewlo imports
from mewlo.mpacks.core.site import msitemanager

# helper imports
from testhelpers.testsite1.testsite1 import MewloSite_Test1

# python imports
import unittest




# Our unit test class
class BasicSiteTest(unittest.TestCase):


    def testSimpleSiteInstantiation(self):
        """A simple test that just creates a small sample site and checks for errors."""

        # create sitemanager and start it up
        sitemanager = self.makestart_sitemanager()

        # fail or pass test depending on if there were any preparation errors
        self.failIf(sitemanager.prepeventlist.count_errors() > 0)

        # shutdown sitemanager and site
        sitemanager.shutdown()






    def makestart_sitemanager(self):
        """Support helper function for tests."""

        # start up in debug mode?
        debugmode = True

        # Create a site manager and ask it to instantiate a site of the class we specify
        sitemanager = msitemanager.MewloSiteManager(debugmode, MewloSite_Test1)

        # startup site - this will generate any preparation errors
        sitemanager.startup()

        # check for errors
        if (sitemanager.prepeventlist.count_errors() > 0):
            print "Site manager preparation error events:"
            print sitemanager.prepeventlist.dumps()

        # return it
        return sitemanager









# if this python file is run as a script:

def main():
    # defer to unit test tool
    unittest.main()

if __name__ == '__main__':
    main()


