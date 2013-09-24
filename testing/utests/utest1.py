# utest1.py
# unit teests


# mewlo imports

# helper imports


# python imports
import unittest




# Our unit test class
class BasicSiteTest(unittest.TestCase):


    def testOne(self):
        from testhelpers.testsite1.testsite1 import MewloSite_Test1
        #
        sitemanager = MewloSite_Test1.create_manager_and_simplesite()
        #
        if (sitemanager.prepeventlist.count_errors() > 0):
            print "Site manager preparation error events:"
            print sitemanager.prepeventlist.dumps()
        #
        self.failIf(sitemanager.prepeventlist.count_errors() > 0)


    def testTwo(self):
        self.failUnless(True)




# if this python file is run as a script:

def main():
    # defer to unit test tool
    unittest.main()

if __name__ == '__main__':
    main()


