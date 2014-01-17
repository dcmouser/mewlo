"""
manager.py

A base class for high-level site-helping managers.
"""






class MewloManager(object):
    """Base class for high-level site-helping managers; base class does little."""

    def __init__(self):
        self.mewlosite = None


    def startup(self, mewlosite, eventlist):
        """Startup everything."""
        self.mewlosite = mewlosite
        self.mewlosite.logevent("Startup of manager ({0}).".format(self.__class__.__name__))


    def shutdown(self):
        """Shutdown everything, we are about to exit."""
        self.mewlosite.logevent("Shutdown of manager ({0}).".format(self.__class__.__name__))
        pass



    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = " "*indent + "MewloManager (" + self.__class__.__name__ + ") reporting in.\n"
        return outstr