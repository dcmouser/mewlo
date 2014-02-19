"""
manager.py

A base class for high-level site-helping managers.
"""






class MewloManager(object):
    """Base class for high-level site-helping managers; base class does little."""

    def __init__(self, mewlosite, debugmode):
        """
        Initialization/construction of a manager
        When this happens you should never do much -- because you may have no idea what other managers/components have been created yet.
        """
        self.mewlosite = mewlosite


    def prestartup_register_dbclasses(self, mewlosite, eventlist):
        """
        This is called for all managers, before any managers get startup() called.
        By the time this gets called you can be sure that ALL managers/components have been added to the site.
        The most important thing is that in this function managers create and register any database classes BEFORE they may be used in startup.
        The logic is that all managers must register their database classes, then the database tables will be build, then we can proceed to startup.
        """
        pass


    def startup(self, eventlist):
        """Startup everything."""
        self.mewlosite.logevent("Startup of manager ({0}).".format(self.__class__.__name__))


    def poststartup(self, eventlist):
        """Called after all managers finish with startup()."""
        pass


    def shutdown(self):
        """Shutdown everything, we are about to exit."""
        self.mewlosite.logevent("Shutdown of manager ({0}).".format(self.__class__.__name__))
        pass




    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = " "*indent + "MewloManager (" + self.__class__.__name__ + ") reporting in.\n"
        return outstr
    
    
    
    

    def get_setting_value(self, sectionmame, defaultval=None):
        return self.mewlosite.settings.get_value(sectionmame, defaultval)

    
    def get_setting_subvalue(self, sectionmame, varname, defaultval=None):
        return self.mewlosite.settings.get_subvalue(sectionmame, varname, defaultval)