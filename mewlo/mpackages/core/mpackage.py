"""
mpackage.py
This file defines the classes that support mewlo package/extensions
"""




# helper imports
import helpers.pkg.packagemanager as packagemanager
import helpers.pkg.package as package



# global constants
DefMewlo_Package_filepatternsuffix = "mpackage"





class MewloPackage(package.Package):
    """
    The MewloPackage class represents an mewlo "package" aka extension/plugin/addon/component.
    It is *not* the same as a Python "package".
    All code (both core builtin code and 3rd party extensions/plugins) is always in the form of a mewlo package.
    The MewloPackage class exposes author and version info about a package, supports online, version checking, database updating, dependency chains, etc.
    """

    def __init__(self, packagemanager, filepath):
        super(MewloPackage, self).__init__(packagemanager, filepath)










class MewloPackageManager(packagemanager.PackageManager):
    """
    The MewloPackageManager manages a collection of MewloPackages.
    """

    def __init__(self, mewlosite):
        # parent constructor
        super(MewloPackageManager,self).__init__()
        # set pointer to mewlosite
        self.mewlosite= mewlosite
        # set file pattern of mewlo package files
        self.set_filepatternsuffix(DefMewlo_Package_filepatternsuffix)


    def create_package(self, filepath):
        """Create an appropriate child package."""
        return MewloPackage(self,filepath)










class MewloPackageObject(packagemanager.PackageObject):
    """
    The MewloPackageObject class is the parent class for the actual 3rd party class that will be instantiated when a package is LOADED+ENABLED
    """

    def __init__(self, package):
        super(MewloPackageObject, self).__init__(package)









