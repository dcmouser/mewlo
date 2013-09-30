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
MewloGlobals = {
    'site': None,
    'flag_debugmode_enabled': True,
    }




# shortcut functions for common stuff


def mewlosite():
    global MewloGlobals
    return MewloGlobals['site']
def set_mewlosite(val):
    global GLOBAL_mewlosite
    MewloGlobals['site'] = val


def debugmode():
    #ATTN: might it be better to have this ask the SITE if its debugging?
    global MewloGlobals
    return MewloGlobals['flag_debugmode_enabled']
def set_debugmode(val):
    #ATTN: might it be better to have this ask the SITE if its debugging?
    global MewloGlobals
    MewloGlobals['flag_debugmode_enabled'] = val