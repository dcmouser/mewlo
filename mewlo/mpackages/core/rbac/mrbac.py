"""
mrbac.py
This module contains classes and functions to manage the RBAC/ACL (permission) system.
ATTN: UNFINISHED
"""


# mewlo imports
from ..database import mdbmodel
from ..database import mdbfield
from ..database import mdbmixins
from ..manager import manager

# python imports






class MewloRole(mdbmodel.MewloDbModel):
    """The role class manages hierarchy of roles."""

    # class variables
    dbtablename = 'role_def'
    dbschemaname = 'default'

    @classmethod
    def define_fields(cls, dbmanager):
        """This class-level function defines the database fields for this model -- the columns, etc."""

        # define fields list
        fieldlist = [
            # standard primary id number field
            mdbfield.DbfPrimaryId('id', {
                'label': "The primary key and id# for this row"
                }),
            # enabled?
            mdbfield.DbfBoolean('is_enabled', {
                'enabled': "Is this rule enabled?"
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
            # and now relations for role hierarchy
            mdbfield.Dbf_SelfSelfRelation('childroles',{
                'associationclass': MewloRoleHierarchy,
                'otherclass': MewloRole,
                'backrefname': 'parentroles',
                'primaryjoin_name': 'parent_id',
                'secondaryjoin_name': 'child_id',
                }),
             ]

        return fieldlist






class MewloRoleHierarchy(mdbmodel.MewloDbModel):
    """The role class manages hierarchy of roles."""

    # class variables
    dbtablename = 'role_hierarchy'
    dbschemaname = 'default'

    @classmethod
    def define_fields(cls, dbmanager):
        """This class-level function defines the database fields for this model -- the columns, etc."""

        # define fields list
        fieldlist = [
            # standard primary id number field
            mdbfield.DbfPrimaryId('id', {
                'label': "The primary key and id# for this row"
                }),
            # a unique short text keyname
            mdbfield.DbfForeignKey('parent_id', {
                'label': "The parent role id",
                'foreignkeyname': MewloRole.get_dbtablename()+'.id',
                }),
            # text label
            mdbfield.DbfForeignKey('child_id', {
                'label': "The child role id",
                'foreignkeyname': MewloRole.get_dbtablename()+'.id',
                }),
             ]

        return fieldlist











class MewloRoleAssignment(mdbmodel.MewloDbModel):
    """The role class manages hierarchy of roles."""

    # class variables
    dbtablename = 'role_assign'
    dbschemaname = 'default'

    @classmethod
    def define_fields(cls, dbmanager):
        """This class-level function defines the database fields for this model -- the columns, etc."""

        # define fields list
        fieldlist = [
            # standard primary id number field
            mdbfield.DbfPrimaryId('id', {
                'label': "The primary key and id# for this row"
                }),
            # subject gob
            mdbmixins.dbfmixin_gobreference('subject'),
            # role
            mdbfield.Dbf1to1_OneWay('role_id', {
                'rightclass': MewloRole,
                'relationname': 'role',
                }),
            # resource gob
            mdbmixins.dbfmixin_gobreference('resource'),
            ]

        return fieldlist






















class MewloRbacManager(manager.MewloManager):
    """The Rbac system manager."""

    def __init__(self, mewlosite, debugmode):
        """Constructor."""
        super(MewloRbacManager,self).__init__(mewlosite, debugmode)

    def startup(self, eventlist):
        super(MewloRbacManager,self).startup(eventlist)

    def shutdown(self):
        super(MewloRbacManager,self).shutdown()


