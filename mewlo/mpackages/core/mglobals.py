"""
mglobals.py
This file contains classes to handle Mewlo sites and site manager.any globals the system uses
"""


# We want to avoid the use of global variables like the plague
#  but there are some rare scenarios where we have a quantity that we may need to access from any arbitrary function and where it's just not practical to pass around objects to facilitate lookup
# Use:
# from mewlo.mpackages.core.mglobals import mewlosite
# site = mewlosite()
#


# All mewlo globals go in this dictionary
# But as a point of fact, i think we prefer to have NO globals other than the site, and let the site object hold anything else that might otherwise be considered a "global"





class MewloGlobalClass:
    # all global state data is stored in this class data
    globals = {
        'site': None,
        }
    #
    @classmethod
    def onimport(cls):
        # This is so evil.. Python is reloading this module randomly after we dynamically import a module by pathname
        # Which means it RESETS global and class data.  This means that NO module can EVER rely on any module-level persistent data being preserved?!
        # So we save and load it to system state on reload.  F*CKING RIDICULOUS.  PYTHON IS MAGIC!! MAGICALLY FUCKED.
        import sys
        try:
            # try to retrieve saved data from sys module
            MewloGlobalClass.globals = sys.mewloglobals
        except AttributeError:
            # on exception, it's first time, so store reference to our data in sys module
            sys.mewloglobals = MewloGlobalClass.globals

# call this class method every time this module is imported
# note that due to some very strange python behavior (i called it a messed up f*cking bug),
#  this module can be reloaded after another dynamic extension is loaded, causing it to lose any static class data,
#  meaning this function will get called multiple times.
MewloGlobalClass.onimport()





# shortcut functions for common stuff


def mewlosite():
    """Return the global MewloSite reference."""
    return MewloGlobalClass.globals['site']

def set_mewlosite(val):
    """Set global MewloSite reference (other "globals" depend on this)."""
    MewloGlobalClass.globals['site'] = val



def debugmode():
    """Return True if debugmode is enabled -- note that we let the SITE track the actual debugmode variable."""
    return mewlosite().get_debugmode()

def set_debugmode(val):
    """Set global (site) debugmode."""
    mewlosite().get_debugmode()



def db():
    """Return reference to site database manager."""
    return mewlosite().dbmanager


def notfinished(msg):
    """Shortcut function to log a not finished message."""
    from helpers.event.event import EWarning
    mewlosite().logevent(EWarning(msg))


