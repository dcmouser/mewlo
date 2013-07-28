# test1.py
# It's useful to try invoking python test.py from this main demosites directory, in order to verify that relative importing works for the test site, regardless of whether it is run as main script or from an import


# Mewlo imports
from test1 import testsite1







# if this python file is run as a script:

def main():
    # just invoke main() in testsite1
    testsite1.main()

if __name__ == "__main__":
    main()


