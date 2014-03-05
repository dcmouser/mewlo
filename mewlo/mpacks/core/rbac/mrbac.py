"""
mrbac.py
This module contains classes and functions to manage the RBAC/ACL (permission) system.

The documentation discusses the RBAC system in more detail.

Essentially we have 3 tables that work together to build an RBAC system:

1. Role definitions (role_def table; MewloRole class).
2. Role hierarchy (role_hierarchy table; MewloRoleHierarchy class).
3. Role assignments (role_assign table; MewloRoleAssignment class).

The Role definitions table actually defines roles; this gives each role a name, id, and description.  An example of a role might be "IsOwnerOfGroup".
Note that the role definition does NOT refer to a specific resource (specific group) or subject (specific user).

The Role hierarchies table establishes a hierarchy of role DEFINITIONS.  That is, role (definitions) may be parents of one another.
Child roles inherit permissions of the parents.
This is a very simple table that simply definines which role definitions are parents of which others.  If role A is a parent of role B, we say that role A entails role B.
Note that we allow role definitions to be children of multiple parents.
Note that our hierarchy describes a relationship between role DEFINITIONS (not actual assignments).  That is, we can say the the role of "Group Ownership" is a parent of "Group Membership".
Note that the key purpose of hierarchies is implying role assignments for children roles.
For example, if role A is a parent of role B, and user X has role A, then user X also has role B.

Note that role hierarchies express a very limited form of relationships of role implication (entitlement).
By that I mean that we cannot express arbitrary entitlements like "Having role #45 on resource #67 entails having role #48 on resource #910."
The most we can say is that "Having role #45 entails having role #48" or equivelently, that "Having role #45 on resource #67 entails having role #48 on resource #67."


The Role assignment table assigns a specific role (definition) to a specific subject (typically a user), and possibly restricted to a specific resource object.
Some example role assignments:
    "Subject #123 (user X) has role #45 (IsOwnerOfGroup) for resource #67 (group y)."
    "Subject #123 (user X) has role #1 (IsAdmin)."
    "Subject #67 (group y) has role #23 (IsParentGroup) for resouce #68 (group z)."

Some kinds of queries we might ask the RBAC system:
    "Does subject #123 have role #45 for resource #67?"
    "What roles does subject #123 have for resource #67?"
    "What subjects have role #45 on resource #67?"
    "What roles does subject #123 have?"
    "What subject roles are held on resource #67?"
    "What subjects and resources are using role #45?"

It is important to note that the role hierarchy makes queries non-trivial.
So if we ask "Does subject #123 have role #45 for resource #67?", this should be understood as "Does subject have role #45, or any parent role of role #45, for resource #67 (or for all resources)?"

There are some common things that will require multiple steps to check.
For example, let's say we wanted to know if Subject #123 had role #40 (edit) for resource #600 (which was a blog page in group #67.

In addition to checking for the permission directly on resource 600, this might require that we check if subject has role #41 (edit group-owned blogs) on group #67.
This check is something that the coder would have to perform -- the RBAC system itself does not know that this "group role" implies a role on the specific object.

If we *DID* want to extend the RBAC system to handle such scenarios automatically, it would require an extension that allowed us to express relationships like:
  "Role #r1 held by subject s1 (of TYPE S1) on resource r1 (of type R1), implies role #r2 by subject s2 on resource r2, where some set of role assignments constain s1,s2,r1,r2."
  or in our example above: "Rule #isadmin held by subject s1 (of type USER) on resource r1 (of type GROUP), implies role #canedit by subject s1 on resource r2 (of type BLOG), where r2 hasrole #isownedby on resource r1"
  We judge that the complications of expressing such relationships is best handled in code rather than automatically in the RBAC system, and restrict the RBAC system to the simpler cases.

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

    # class constants
    description = "Handles the authorization and permission API"
    typestr = "core"


    def __init__(self, mewlosite, debugmode):
        """Constructor."""
        super(MewloRbacManager,self).__init__(mewlosite, debugmode)

    def startup(self, eventlist):
        super(MewloRbacManager,self).startup(eventlist)

    def shutdown(self):
        super(MewloRbacManager,self).shutdown()









    def does_subject_have_role(self, subject, role):
        """Just shortcut to does_subject_have_role_on_resource()."""
        return self.does_subject_have_role_on_resource(subject, role, None)


    def does_subject_have_role_on_resource(self, subject, role, resource):
        """Return True if user has a role on an object.
        This includes looking at role hierarchies and group memberships for user."""

        # our first step is to convert args to id#s
        # we allow caller to pass us subject, role, resource as a pre-resolved id#, OR as an object with a gobid (for subject, resource), OR as a role object, role id, or string for role.
        # note that subject CANNOT be a userid (if it's an id, it must be a gobid)
        # for our db search we want subject and resource to GOBids (there are our globally unique numeric identifiers in the gob table).
        # for our db search we want role as as role id#

        # get subject and resource gobids (#ATTN: TODO for efficiency we might want to make this a single OR db query in the future), and role id
        subjectid = self.lookup_gobid(subject)
        resourceid = self.lookup_gobid(resource)
        roleid = self.lookup_roleid(role)

        # list of role ids that entail our roleid
        roleids = self.lookup_entailing_roles(roleid)

        #ok now we have subject gobid#, resource gobid# (or NONE) and role id#
        # get any assignments that match
        # ATTN: later do this more efficiently
        assignmentids = self.lookup_roleassignids([subjectid], roleids, [resourceid])

        if (assignmentids):
            return True

        # no assignmentids, so it's false
        return False



    def lookup_roleassignids(self, subjectids, roleids, resourceids):
        """Return list of role assignments where any of subjectids has any of roleids on any of resourceids or on resourceid==None."""

        # always add None to list of resourceids, because an assignment which has None for the resource, means for ALL resources
        if (not None in resourceids):
            resourceids.append(None)

        # build filter dictionary for role assignments
        filterdict = {'subject_gobid': subjectids,
                      'resource_gobid': resourceids,
                      'role_id': roleids}
        # ATTN: TODO - use a non-orm search for ids for efficiency
        assignments = MewloRoleAssignment.find_all_bykey_within(filterdict)
        assignmentids = [x.id for x in assignments]
        return assignmentids




    def lookup_gobid(self, obj):
        """obj may be None, integer (gobid), or an object with a gobid property."""
        if (obj == None):
            return None
        if (isinstance(obj, int)):
            return obj
        if (hasattr(obj,'gobid')):
            return obj.gobid
        raise Exception("ERROR: do not know how to look up gobid from object {0}.".format(str(obj)))


    def lookup_roleid(self, role):
        """obj may be None, integer (gobid), or an object with a gobid property."""
        if (role == None):
            return None
        if (isinstance(role, (long,int))):
            return role
        if (isinstance(role,basestring)):
            return self.lookup_roleid_byname(role)
        if (isinstance(role, MewloRole)):
            return role.id
        raise Exception("ERROR: do not know how to look up roleid from role {0}.".format(str(role)))


    def lookup_roleid_byname(self, rolename):
        """lookup a role by name."""
        # ATTN: TODO - for now we use orm but later we will want to do a direct fast-as-possible query for id
        role = self.lookup_role_byname(rolename)
        if (role == None):
            return None
        return role.id


    def lookup_role_byname(self, rolename):
        """lookup a role by name."""
        role = MewloRole.find_one_bykey({'name':rolename})
        return role




    def lookup_entailing_roles(self, roleid):
        """return a list of roleids that entail this one (including itself)."""
        # ATTN: TODO - in the future we can store a special table of FLATTENED CACHED hierarchy so that we can do this always with a single lookup
        if (roleid == None):
            return [None]

        # start with ourself
        entailingroleids = []

        # loop adding roles until there are no more to add
        addroleids = [roleid]
        while (addroleids):
            # we have some new roles to add,
            # search for parents of addroles
            parentroleids = self.lookup_parentroleids(addroleids)
            #print "ATTN parents of {0} are {1}.".format(str(addroleids),str(parentroleids))
            # now add addroles
            entailingroleids = entailingroleids + addroleids
            # and new parents not already in our entailing list, are the next roles to add and lookup
            if (parentroleids):
                addroleids = list(set(parentroleids)-set(entailingroleids))
            else:
                addroleids = None

        #print "Entailing roles for {0} are {1}.".format(roleid,str(entailingroleids))

        # return list
        return entailingroleids


    def lookup_parentroleids(self, roleids):
        """return a list of parent roleids which are parents to any elements in roleids."""
        # ATTN: TODO - use a non-orm search for ids for efficiency
        parentroles = MewloRoleHierarchy.find_all_bykey_within({'child_id':roleids})
        parentroleids = [x.id for x in parentroles]
        return parentroleids








    def create_role(self, rolename):
        """Create a new role."""
        role = MewloRole()
        role.name = rolename
        # save it
        role.save()
        # return it
        return role



    def create_assignment(self, subject, role, resource=None):
        """Create a new assignment."""

        # our first step is to convert args to id#s
        # we allow caller to pass us subject, role, resource as a pre-resolved id#, OR as an object with a gobid (for subject, resource), OR as a role object, role id, or string for role.
        # note that subject CANNOT be a userid (if it's an id, it must be a gobid)
        # for our db search we want subject and resource to GOBids (there are our globally unique numeric identifiers in the gob table).
        # for our db search we want role as as role id#

        # get subject and resource gobids (#ATTN: TODO for efficiency we might want to make this a single OR db query in the future), and roleid
        subjectid = self.lookup_gobid(subject)
        resourceid = self.lookup_gobid(resource)
        roleid = self.lookup_roleid(role)

        # create it
        assignment = MewloRoleAssignment()
        assignment.subject_gobid = subjectid
        assignment.resource_gobid = resourceid
        assignment.role_id = roleid
        # save it
        assignment.save()
        # return it
        return assignment



    def create_roleentails(self, role_parent, role_child):
        """Add a role hierarchy relation."""

        # lookup args
        role_parent_id = self.lookup_roleid(role_parent)
        role_child_id = self.lookup_roleid(role_child)

        # creat it
        rolerelation = MewloRoleHierarchy()
        rolerelation.parent_id = role_parent_id
        rolerelation.child_id = role_child_id
        # save it
        rolerelation.save()
        # return it
        return rolerelation


