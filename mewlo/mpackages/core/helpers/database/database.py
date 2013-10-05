"""
database.py

This is our database helper module

"""


# helper imports

# python imports







class DbHelper(object):
    """A component object that helps manage our database operations."""

    def __init__(self):
        """Constructor."""
        # init
        pass


    def startup(self):
        #print "**** IN DbHelper STARTUP ****"
        pass

    def shutdown(self):
        #print "**** IN DbHelper SHUTDOWN ****"
        pass




    def dumps(self, indent=0):
        """Debug information."""
        outstr = " "*indent + "DbHelper (" + self.__class__.__name__  + ") reporting in.\n"
        return outstr




