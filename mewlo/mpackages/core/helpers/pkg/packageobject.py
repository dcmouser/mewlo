# package.py
# Works with packagemanager.py to support our package/extension/addon system






class PackageObject(object):
    """
    The PackageObject class is the parent class for the actual 3rd party class that will be instantiated when a package is LOADED+ENABLED
    """

    def __init__(self, in_package):
        self.package = in_package


    def debug(self,indentstr=""):
        outstr = indentstr+"Base PackageObject reporting in.\n"
        return outstr


