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
        self.viewbasepath = '${addon_group_path}/views/'
        #
        # we all of our non-form view files here, so that they are in one place (the forms themselves can specify their own default view files -- see form.get_viewfilename())
        self.viewfiles = {
            'grouplist' : 'grouplist.jn2',
            'groupinfo' : 'groupinfo.jn2',
            }


































































    def request_grouphome(self, request):
        """Group list."""
        # set page id
        self.set_renderpageid(request, 'grouplist')

        # contents
        groupmanager = self.sitecomp_groupmanager()
        grouplist = groupmanager.modelclass.find_all()

        # then page contents
        self.render_localview( request, self.viewfiles['grouplist'], {'grouplist':grouplist} )







    def request_groupinfo(self, request):
        """Group info."""
        # get args
        groupid = request.get_route_parsedarg('id',None)

        # set page id
        self.set_renderpageid(request, 'groupinfo')

        # contents
        groupmanager = self.sitecomp_groupmanager()
        group = groupmanager.modelclass.find_one_byprimaryid(groupid)
        assignments_annotated = groupmanager.get_annotated_assignments_for_group(group)

        # then page contents
        self.render_localview( request, self.viewfiles['groupinfo'], {'group':group, 'assignments_annotated':assignments_annotated} )
