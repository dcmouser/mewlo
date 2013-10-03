# demosite1test.py
# this just invokes the testsite1/testsite1 script which creates the test site and let's it run its default main()
# this is NOT part of the test suite just a quick way of testing standalone site script execution

# Mewlo imports
import testhelpers.testsite1.testsite1 as testsite1






# if this python file is run as a script:

def main():
    # just invoke main() in testsite1
    testsite1.main()

if __name__ == '__main__':
    main()


