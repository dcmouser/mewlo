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

    # class constants
    description = "Handles the group database model"

    def __init__(self, mewlosite, debugmode):
        # parent constructor -- pass in the main modelclass we manager
        super(MewloGroupManager,self).__init__(mewlosite, debugmode, mgroup.MewloGroup, True)











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





