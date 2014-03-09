"""
mgroupmanager.py

The helper manager for group model.

"""



# mewlo imports
from ..manager import modelmanager
from ..helpers import misc
import mgroup
from ..eventlog.mevent import EFailure, EException
from ..constants.mconstants import MewloConstants as mconst

# python imports





class MewloGroupManager(modelmanager.MewloModelManager):
    """Group model manager."""

    def __init__(self, mewlosite, debugmode):
        # parent constructor -- pass in the main modelclass we manager
        super(MewloGroupManager,self).__init__(mewlosite, debugmode, mgroup.MewloGroup)


    def startup(self, eventlist):
        super(MewloGroupManager,self).startup(eventlist)

    def shutdown(self):
        super(MewloGroupManager,self).shutdown()



    def lookup_group_byname(self, groupname):
        """Lookup a group by name."""
        group = self.modelclass.find_one_bykey({'groupname':groupname})
        return group


    def create_group(self, groupname, label, description):
        """Create a new group."""
        group = self.modelclass()
        group.groupname = groupname
        group.label = label
        group.description = description
        group.save()
        return group













    def get_group_rbac_info(self, group):
        """Return some debug info about the users roles."""
        rbacmanager = self.sitecomp_rbacmanager()

        # get all assignments involving the group
        assignments = rbacmanager.lookup_roleassigns_either_subject_or_resource(group,'*')
        # now lookup array of ROLEDEFS for these roles, and then array of OBJECTS involved in these assignments
        roledefarray = rbacmanager.lookup_roledefarray_from_assignments(assignments)
        gobarray = rbacmanager.lookup_gobarray_from_assignments(assignments, roledefarray)

        # build the html
        rbac_info_html = "All role assignments for group:\n<ul>"
        for assignment in assignments:
            assignment_nicedescription = rbacmanager.calc_assignment_nicedescription(assignment, roledefarray, gobarray)
            rbac_info_html += "<li>Role assignment: {0}.</li>\n".format(assignment_nicedescription)
        if (not assignments):
            rbac_info_html += "<li>NONE</li>\n"
        rbac_info_html += "</ul>\n"

        return rbac_info_html
