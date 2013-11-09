"""
mrbac.py
This module contains classes and functions to manage the RBAC/ACL (permission) system.

"""


# mewlo imports
from ..database import mdbmodel
from ..database import mdbmodel_relation
from ..database import mdbfield

# python imports






class MewloRole(mdbmodel.MewloDbModel):
    """The role class manages hierarchy of roles."""

    # class variables
    dbtablename = 'roles'
    dbschemaname = 'default'

    @classmethod
    def definedb(cls, dbmanager):
        """This class-level function defines the database fields for this model -- the columns, etc."""

        # now add our fields
        fieldlist = cls.fieldlist

        # define fields list
        fieldlist = [
            # standard primary id number field
            mdbfield.DbfPrimaryId('id', {
                'label': "The primary key and id# for this row"
                }),
            # a unique short text keyname
            mdbfield.DbfUniqueKeyname('name', {
                'label': "The unique name for this role"
                }),
            # text label
            mdbfield.DbfString('label', {
                'label': "The description label for this role"
                }),
            # an arbitrarily long string serializing any role properties that we don't have explicit fields for.
            mdbfield.DbfSerialized('serialized_fields', {
                'label': "The serialzed text version of any extra properties"
                }),
             ]

        cls.hash_fieldlist(fieldlist)








class MewloRbacManager(object):
    """The Rbac system manager."""

    def __init__(self):
        """Constructor."""
        pass

    def startup(self, mewlosite, eventlist):
        self.mewlosite = mewlosite

    def shutdown(self):
        pass




    def register_role_assignment_class(self, roleassignmentclass):
        """Register a new role assignment class."""
        pass