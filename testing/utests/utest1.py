# utest1.py
# This is a unit test module for mewlo
#
# It uses the python unittest framework to manage test running and reporting


# mewlo imports

# helper imports

# python imports
import unittest




# Our unit test class
class BasicSiteTest(unittest.TestCase):


    def testSimpleSiteInstantiation(self):
        """A simple test that just creates a small sample site and checks for errors."""

        # Instantiate a test site and see if there were any startup errors
        from testhelpers.testsite1.testsite1 import MewloSite_Test1
        sitemanager = MewloSite_Test1.create_manager_and_simplesite()

        # startup site - this will generate any preparation errors
        sitemanager.startup()

        # check for errors
        if (sitemanager.prepeventlist.count_errors() > 0):
            print "Site manager preparation error events:"
            print sitemanager.prepeventlist.dumps()

        # fail or pass test depending on if there were any preparation errors
        self.failIf(sitemanager.prepeventlist.count_errors() > 0)

        # shutdown
        sitemanager.shutdown()


    def testTwo(self):
        self.failUnless(True)




# if this python file is run as a script:

def main():
    # defer to unit test tool
    unittest.main()

if __name__ == '__main__':
    main()


