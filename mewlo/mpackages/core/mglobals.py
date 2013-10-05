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
    globals = {
        'site': None,
        }
    @classmethod
    def onimport(cls):
        # This is so fucking evil.. Python is reloading this module randomly after we dynamically import a module by pathname
        # Which means it RESETS global and class data.  This means that NO module can EVER rely on any module-level persistent data being preserved
        # So we save and load it to system state on reload.  FUCKING RIDICULOUS.  PYTHON IS MAGIC!! MAGICALLY FUCKED.
        import sys
        try:
            MewloGlobalClass.globals = sys.mewloglobals
        except AttributeError:
            sys.mewloglobals = MewloGlobalClass.globals
#
MewloGlobalClass.onimport()


# shortcut functions for common stuff


def mewlosite():
    #print "---> ASKING GLOBAL MEWLO RETURNING "+str(MewloGlobalClass.globals['site'])
    return MewloGlobalClass.globals['site']

def set_mewlosite(val):
    #print "---> SETTING GLOBAL MEWLO SITE TO "+str(val)
    MewloGlobalClass.globals['site'] = val



def debugmode():
    #ATTN: do we want to use a true global or ask the site for its setting?
    return mewlosite().get_debugmode()

def set_debugmode(val):
    #ATTN: do we want to use a true global or ask the site for its setting?
    mewlosite().get_debugmode()