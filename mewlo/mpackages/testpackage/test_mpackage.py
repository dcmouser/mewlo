# test_mpackage.py
# This file manages a test package

# mewlo imports
import mewlo.mpackages.core.mpackage as mpackage



class Test_MewloPackageObject(mpackage.MewloPackageObject):
    """
    The Test_MewloPackage class defines a test mewlo "package" aka extension/plugin/addon.
    """

    def __init__(self, in_package):
        super(Test_MewloPackageObject, self).__init__(in_package)
        pass


    def debug(self,indentstr=""):
        str = indentstr+"Mewlo Test_MewloPackage reporting in.\n"
        return str

