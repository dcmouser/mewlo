"""
mrbac_rolemn.py
This module contains classes and functions to manage the RBAC/ACL (permission) system.

NOTE: This class is no longer used -- it was written when we were anticipating a multi-table approach to storing role assignments.

"""


# mewlo imports
from ..database import mdbmodel
from ..database import mdbmodel_relation
from ..database import mdbfield

# python imports






class RbacRoleAssignment_MN(mdbmodel_relation.MewloDbRelationModel_FullMtoN):
    """The role class manages hierarchy of roles."""


    @classmethod
    def setup_roleassignment_classes(cls, leftclass, rightclass):
        """Setup the role assignment class."""
        cls.set_sideclasses(leftclass, rightclass)
        tablename = 'roleassign_' + leftclass.get_dbtablename() + '_' + rightclass.get_dbtablename()
        cls.override_dbnames(tablename, 'default')


    @classmethod
    def definedb(cls, dbmanager):
        """This class-level function defines the database fields for this model -- the columns, etc."""

        # call parent define
        super(RbacRoleAssignment_MN,cls).definedb(dbmanager)

        # now add our fields
        fieldlist = cls.fieldlist

        # define fields list
        fieldlist.extend( [
            # in addition to being an MxN mapper between left and right classes
            # a role assignment contains a reference to a particial role id
            mdbfield.Dbf1toN_Right('role_id', {
                'label': "The id of the role",
                'leftclass': MewloRole,
                }),
            # an arbitrarily long string serializing any role properties that we don't have explicit fields for.
            mdbfield.DbfSerialized('serialized_fields', {
                'label': "The serialzed text version of any extra properties"
                }),
             ])
        cls.hash_fieldlist(fieldlist)



    @classmethod
    def create_helpermodels(cls, dbmanager):

        # and we need to add an item to the left hand class (could we not do this all in one?)
        # ATTN: this is not working yet
        leftfields = [
            mdbfield.Dbf1toN_Left(cls.get_dbtablename(),{
                'rightclass':cls,
                'backrefname':'role'}),
            ]
        MewloRole.extend_extrafields(leftfields)


