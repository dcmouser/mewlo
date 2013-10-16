"""
dbmanager.py

This is our database helper module

"""


# helper imports


# python imports







class DatabaseManager(object):
    """A component object that helps manage our database operations."""

    def __init__(self):
        """Constructor."""
        # init
        self.databasesettings = {}


    def startup(self):
        pass

    def shutdown(self):
        pass


    def set_databasesettings(self, databasesettings):
        self.databasesettings = databasesettings



    def dumps(self, indent=0):
        """Debug information."""
        outstr = " "*indent + "DatabaseManager (" + self.__class__.__name__  + ") reporting in.\n"
        outstr += " "*indent + " Settings: "+str(self.databasesettings)
        return outstr


    def resolve(self, text):
        return text


