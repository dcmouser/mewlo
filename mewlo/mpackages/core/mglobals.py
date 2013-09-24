"""
mglobals.py
This file contains classes to handle Mewlo sites and site manager.any globals the system uses
"""


# The one global variable in the entire system
# use:
# from mewlo.mpackages.core.mglobals import mewlosite
# site = mewlosite()
#
GLOBAL_mewlosite = None
#
def mewlosite():
    global GLOBAL_mewlosite
    return GLOBAL_mewlosite
def set_mewlosite(mewlosite):
    global GLOBAL_mewlosite
    GLOBAL_mewlosite = mewlosite


