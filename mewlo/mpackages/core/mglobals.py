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
        # This is so evil.. In certain weird situations python does some very f*cked up stuff and reloads modules or reloads and shadows them
        # See here for why this is happening:
        #  http://stackoverflow.com/questions/4798589/what-could-cause-a-python-module-to-be-imported-twice
        # It's important we not let this happen and overwrite our global/class/static data.
        # We could employ a workaround hiding a copy of our globals in system and restoring it on reload.
        # For now we shall DETECT this occuring and raise an execption
        # Hopefully it will never happen but if it does we want to catch it early.
        import sys
        try:
            # try to retrieve saved data from sys module
            MewloGlobalClass.globals = sys.mewloglobals
            # if we are here, it means this python evilness is in play
            msg = "\n\n\n\n\n----------------------> MEWLO WARNING - DETECTED THAT PYTHON IS MULTIPLY RELOADING MODULESS <---------------------------"
            msg += "THIS CAN HAVE UNPREDICTABLE EFFECTS.  See mewlo.mpackages.core.mglobals for more information.\n\n\n\n\n"
            print msg
            raise Exception(msg)
        except AttributeError:
            # on exception, it's first time, so store reference to our data in sys module
            sys.mewloglobals = MewloGlobalClass.globals














# call this class method every time this module is imported
# note that due to some very strange python behavior (i called it a messed up f*cking bug),
#  this module can be reloaded after another dynamic extension is loaded, causing it to lose any static class data,
#  meaning this function will get called multiple times.
MewloGlobalClass.onimport()













# shortcut functions for common stuff


def UNUSED_mewlosite():
    """Return the global MewloSite reference."""
    return MewloGlobalClass.globals['site']

def set_mewlosite(val):
    """Set global MewloSite reference (other "globals" depend on this)."""
    MewloGlobalClass.globals['site'] = val



def UNUSED_debugmode():
    """Return True if debugmode is enabled -- note that we let the SITE track the actual debugmode variable."""
    return mewlosite().get_debugmode()

def set_debugmode(val):
    """Set global (site) debugmode."""
    mewlosite().get_debugmode()



def UNUSED_db():
    """Return reference to site database manager."""
    return mewlosite().dbmanager


def notfinished(msg):
    """Shortcut function to log a not finished message."""
    from eventlog.mevent import EWarning
    mewlosite().logevent(EWarning(msg))


