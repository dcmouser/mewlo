"""
msiteaddon_group_manager.py
This file contains helper code for group addon stuff
"""


# mewlo imports
from mewlo.mpacks.core.manager import manager
from mewlo.mpacks.core.form.mform import MewloForm
from mewlo.mpacks.core.user import muser, musermanager
from mewlo.mpacks.core.eventlog.mevent import EFailure, EException
from mewlo.mpacks.core.eventlog import mewloexception
from mewlo.mpacks.core.constants.mconstants import MewloConstants as mconst


# python imports
import time





class GroupAddonManager(manager.MewloManager):
    """This class is used to help processing requests.
    """

    # class constants
    description = "Group management addon provides functions for groups"
    typestr = "siteaddon"



    def __init__(self, mewlosite, debugmode):
        """Constructor."""
        super(GroupAddonManager,self).__init__(mewlosite, debugmode)
        #
        self.registration_mode = None
        #
        self.viewbasepath = '${addon_account_path}/views/'
        #
        # we all of our non-form view files here, so that they are in one place (the forms themselves can specify their own default view files -- see form.get_viewfilename())
        self.viewfiles = {
            }


    def startup(self, eventlist):
        super(GroupAddonManager,self).startup(eventlist)

    def shutdown(self):
        super(GroupAddonManager,self).shutdown()











































































    def request_group(self, request):
        """Group info."""
        pass