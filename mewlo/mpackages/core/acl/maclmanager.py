"""
maclmanager.py
This module contains classes and functions to manage the ACL (access control list) system.

"""


# mewlo imports
from ..database import mdbmodel
from ..database import mdbmodel_relation
from ..database import mdbfield

# python imports






class AclRole(mdbmodel.MewloDbModel):
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
             ]

        cls.hash_fieldlist(fieldlist)





class AclRoleAssignment_MN(mdbmodel_relation.MewloDbRelationModel_FullMtoN):
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
        super(AclRoleAssignment_MN,cls).definedb(dbmanager)

        # now add our fields
        fieldlist = cls.fieldlist

        # define fields list
        fieldlist.extend( [
            # in addition to being an MxN mapper between left and right classes
            # a role assignment contains a reference to a particial role id
            mdbfield.Dbf1toN_Right('role_id', {
                'label': "The id of the role",
                'leftclass': AclRole,
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
        AclRole.extend_extrafields(leftfields)









class MewloAclManager(object):
    """The ACL system manager."""

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