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



    def __init__(self, mewlosite, debugmode, siteaddon):
        """Constructor."""
        super(GroupAddonManager,self).__init__(mewlosite, debugmode)
        # settings
        self.siteaddon = siteaddon
        self.set_settings_section(siteaddon.get_settings_section())
        #
        self.viewbasepath = siteaddon.calc_alias_varname('views')
        #
        # we put all of our non-form view files here, so that they are in one place (the forms themselves can specify their own default view files -- see form.get_viewfilename())
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
        self.render_localview_byid( request, 'grouplist', {'grouplist':grouplist, 'groupinfofunc':self.groupinfofunc} )


    def groupinfofunc(self, group, request):
        """Return some info for a group."""
        linkhtml = request.build_routelink_byid(linktext= group.groupname, routeid='groupinfo', args= {'id':group.id})
        rethtml = "{0}. {1}".format(group.id, linkhtml)
        return rethtml




    def request_groupinfo(self, request):
        """Group info."""
        # set page id
        self.set_renderpageid(request, 'groupinfo')

        # get args
        groupid = request.get_route_parsedarg('id',None)
        # get the group
        groupmanager = self.sitecomp_groupmanager()
        #group = groupmanager.modelclass.find_one_byprimaryid(groupid)
        group = groupmanager.modelclass.find_one_bynameorid(groupid)
        # get all assignments involving the group
        rbacmanager = self.sitecomp_rbacmanager()
        assignments = rbacmanager.lookup_roleassigns_either_subject_or_resource(group,'*')
        rbacmanager.annotate_assignments(assignments)

        # then page contents
        self.render_localview_byid( request, 'groupinfo', {'group':group, 'assignments':assignments} )


