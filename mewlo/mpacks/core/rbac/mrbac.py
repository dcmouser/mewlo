"""
mrbac.py
This module contains classes and functions to manage the RBAC/ACL (permission) system.

The documentation discusses the RBAC system in more detail.

Essentially we have 3 tables that work together to build an RBAC system:

1. Role definitions (role_def table; MewloRole class).
2. Role entailment (inheritance hierarchy) (role_entail table; MewloRoleEntails class).
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
from ..helpers import misc

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
            mdbfield.DbfLabelString('label', {
                'label': "The description label for this role"
                }),
            # text label
            mdbfield.DbfTypeString('classname_subject', {
                'label': "The name of the object class used in subject of role"
                }),
            # text label
            mdbfield.DbfTypeString('classname_resource', {
                'label': "The name of the object class used in resource of role (or None)"
                }),
            # an arbitrarily long string serializing any role properties that we don't have explicit fields for.
            mdbfield.DbfSerialized('serialized_fields', {
                'label': "The serialzed text version of any extra properties"
                }),
            # and now relations for role hierarchy
            mdbfield.Dbf_SelfSelfRelation('entailedroles',{
                'associationclass': MewloRoleEntails,
                'otherclass': MewloRole,
                'backrefname': 'parentroles',
                'primaryjoin_name': 'parent_id',
                'secondaryjoin_name': 'entailedchild_id',
                }),
             ]

        return fieldlist



    def calc_nice_rbaclabel(self):
        """Nice display accessor."""
        return "role#{0}:{1}".format(self.id, self.label)






class MewloRoleEntails(mdbmodel.MewloDbModel):
    """The role class manages hierarchy of roles."""

    # class variables
    dbtablename = 'role_entail'
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
            mdbfield.DbfForeignKey('entailedchild_id', {
                'label': "The entailed child role id",
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

            mdbfield.DbfPrimaryId('id', {
                'label': "The primary key and id# for this row"
                }),

            mdbmixins.dbfmixin_gobreference('subject', "The subject gobid"),

            mdbfield.Dbf1to1_OneWay('role_id', {
                'rightclass': MewloRole,
                'relationname': 'role',
                }),

            mdbmixins.dbfmixin_gobreference('resource', "The resource gobid"),

            ]

        return fieldlist




    def calc_nice_annotated_html_info(self):
        """Return a nice html string for the assignment, using optional annotated object info."""

        subjectlabel = self.calc_nicelabel_from_objorid('annotated_subject',self.subject_gobid)
        resourcelabel = self.calc_nicelabel_from_objorid('annotated_resource', self.resource_gobid)
        rolelabel = self.calc_nicelabel_from_objorid('annotated_role', self.role_id)
        if (self.resource_gobid != None):
            retstr = "Subject [{0}] has role [{1}] on resource [{2}]".format(subjectlabel, rolelabel, resourcelabel)
        else:
            retstr = "Subject [{0}] has role [{1}]".format(subjectlabel, rolelabel)
        return retstr


    def calc_nicelabel_from_objorid(self, attributename, fallbackid):
        """Return a nice string label for the annotated object."""
        if (hasattr(self,attributename)):
            attr = getattr(self, attributename)
            if (attr != None):
                return attr.calc_nice_rbaclabel()
        return '#{0}'.format(fallbackid)




    def annotate_with_array(self, roledefarray, gobarray):
        """Annotate with roledef and gobarrays."""
        if (self.role_id in roledefarray):
            self.annotated_role = roledefarray[self.role_id]
        else:
            self.annotated_role = None
        if ((self.subject_gobid != None) and (self.subject_gobid in gobarray)):
            self.annotated_subject = gobarray[self.subject_gobid]
        else:
            self.annotated_subject = None
        if ((self.resource_gobid != None) and (self.resource_gobid in gobarray)):
            self.annotated_resource = gobarray[self.resource_gobid]
        else:
            self.annotated_resource = None

































class MewloRbacManager(manager.MewloManager):
    """The Rbac system manager."""

    # class constants
    description = "Handles the authorization and permission API"
    typestr = "core"


    def __init__(self, mewlosite, debugmode):
        """Constructor."""
        super(MewloRbacManager,self).__init__(mewlosite, debugmode)














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
        """Return list of role assignments where any of subjectids has any of roleids on (any of resourceids or on resourceid==None).
        Each of subject, role, resource much match (i.e. it's AND relations)"""
        # ATTN: TODO - use a non-orm search for ids for efficiency
        assignments = self.lookup_roleassigns(subjectids, roleids, resourceids)
        assignmentids = [x.id for x in assignments]
        return assignmentids




    def lookup_roleassigns(self, subjectids, roleids, resourceids):
        """Return list of role assignments where any of subjectids has any of roleids on (any of resourceids or on resourceid==None).
        Each of subject, role, resource much match (i.e. it's AND relations)"""

        # always add None to list of resourceids, because an assignment which has None for the resource, means for ALL resources
        if (not None in resourceids):
            resourceids.append(None)

        # build filter dictionary for role assignments
        filterdict = {'subject_gobid': subjectids,
                      'resource_gobid': resourceids,
                      'role_id': roleids}

        assignments = MewloRoleAssignment.find_all_advanced(filterdict)
        return assignments




    def lookup_roleassigns_either_subject_or_resource(self, obj, role):
        """Return list of role assignments where any of subjectids has any of roleids on (any of resourceids or on resourceid==None).
        Each of subject, role, resource much match (i.e. it's AND relations)"""

        # our first step is to convert args to id#s
        # we allow caller to pass us subject, role, resource as a pre-resolved id#, OR as an object with a gobid (for subject, resource), OR as a role object, role id, or string for role.
        # note that subject CANNOT be a userid (if it's an id, it must be a gobid)
        # for our db search we want subject and resource to GOBids (there are our globally unique numeric identifiers in the gob table).
        # for our db search we want role as as role id#

        # get subject and resource gobids (#ATTN: TODO for efficiency we might want to make this a single OR db query in the future), and role id
        objid = self.lookup_gobid(obj)
        roleid = self.lookup_roleid(role)
        # list of role ids that entail our roleid
        roleids = self.lookup_entailing_roles(roleid)

        # build filter dictionary for role assignments
        filterdict_or1 = {'subject_gobid': objid,
                      'resource_gobid': objid,
                      }
        filterdict_or2 = {'role_id': roleids}
        cnflist = [filterdict_or1, filterdict_or2]

        assignments = MewloRoleAssignment.find_all_bycnf(cnflist)
        return assignments













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
            if (role=='*'):
                return role
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
        if (roleid == '*'):
            # asterisk string matches all
            return [roleid]

        # start with ourself
        entailingroleids = []

        # loop adding roles until there are no more to add
        addroleids = [roleid]
        while (addroleids):
            # we have some new roles to add,
            # search for parents of addroles
            parentroleids = self.lookup_entailingparent_roleids(addroleids)
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


    def lookup_entailingparent_roleids(self, roleids):
        """return a list of parent roleids which are parents to any elements in roleids."""
        # ATTN: TODO - use a non-orm search for ids for efficiency
        parentroles = MewloRoleEntails.find_all_advanced({'entailedchild_id':roleids})
        parentroleids = [x.id for x in parentroles]
        return parentroleids








    def create_role(self, rolename, label, classname_subject, classname_resource=None):
        """Create a new role."""
        role = MewloRole()
        role.name = rolename
        role.label = label
        role.classname_subject = classname_subject
        role.classname_resource = classname_resource
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



    def create_role_entail(self, role_parent, role_entailedchild):
        """Add a role hierarchy relation."""

        # lookup args
        role_parent_id = self.lookup_roleid(role_parent)
        role_entailedchild_id = self.lookup_roleid(role_entailedchild)

        # creat it
        role_entail = MewloRoleEntails()
        role_entail.parent_id = role_parent_id
        role_entail.entailedchild_id = role_entailedchild_id
        # save it
        role_entail.save()
        # return it
        return role_entail








































    def lookup_roledefarray_from_assignments(self, roleassignments):
        """Simply get the roledef objects from the assignments (note that many roleassignments may use same roledef).
        Return as an array indexed by roleid."""
        # get UNIQUE roleids
        roleids = list(set([x.role_id for x in roleassignments]))
        # now get these roledefs
        roledefs = MewloRole.find_all_byprimaryidlist(roleids)
        # and build indexed list of them
        roledefarray = misc.convert_list_to_id_indexed_dict(roledefs)
        return roledefarray



    def lookup_gobarray_from_assignments(self, role_assignments, roledefarray):
        """Return an array of OBJECTS used in either subject or resource part of role assignments (note that many roleassignments may use same pbjects).
        IMPORTANT: role assignments refer to gobids which are unique numeric identifiers that can refer to multiple kinds of objects.
        This function must lookup and instantiate the proper object instance for the gobid.  There are multiple ways to do this, and some may be messy/slow.
        So we may want to be cautious about using this function for important things.
        Return as an array indexed by gobid."""
        # role assignments may use different classes of objects, so our first task will be to arrange all objects referred to in role assignments by class
        gobids_by_class = {}
        for assignment in role_assignments:
            # for each assignment, get the role, and then the class names for the subject and resource
            role = roledefarray[assignment.role_id]
            subject_classname = role.classname_subject
            resource_classname = role.classname_resource
            # now add unique values to each list indexed by classname
            if (subject_classname != None):
                self.add_uniqueval_to_listkey(assignment.subject_gobid, gobids_by_class, subject_classname)
            if (resource_classname != None):
                self.add_uniqueval_to_listkey(assignment.resource_gobid, gobids_by_class, resource_classname)

        # ok now we want to look up the actual objects
        gobarray = {}
        for classname, gobidlist in gobids_by_class.iteritems():
            # lookup object array
            objarray = self.lookup_objarray_by_class_and_gobidlist(classname, gobidlist)
            # merge it with main array
            gobarray.update(objarray)

        # return it
        return gobarray



    def add_uniqueval_to_listkey(self, val, keydict, key):
        """Add id to list indexed by key in keydict."""
        if (not key in keydict):
            keydict[key] = [val]
        elif (not val in keydict[key]):
            keydict[key].append(val)


    def lookup_objarray_by_class_and_gobidlist(self, classname, gobidlist):
        """We are given a classname and a gobidlist; we want to return the objects with matching gobids.
        This is tricky because the classname must be looked up dynamically."""
        # first convert clasname into classmodel
        classmodel = self.lookup_classmodel_from_classname(classname)
        # now fetch matching objects
        objs = classmodel.find_all_bygobidlist(gobidlist)
        # convert to indexed
        #objarray = misc.convert_list_to_id_indexed_dict(objs)
        objarray = misc.convert_list_to_attribute_indexed_dict(objs, 'gobid')
        # return it
        return objarray


    def lookup_classmodel_from_classname(self, classname):
        """Find the MewloModel derived CLASS specified by classname."""
        classmodel = self.sitecomp_dbmanager().lookupclass(classname)
        return classmodel












    def annotate_assignments(self, assignments):
        """Given a list of assignments, annotate them with real info about the roles and objects involved."""
        # now lookup array of ROLEDEFS for these roles, and then array of OBJECTS involved in these assignments
        roledefarray = self.lookup_roledefarray_from_assignments(assignments)
        gobarray = self.lookup_gobarray_from_assignments(assignments, roledefarray)
        # now annotate the assignments with the objects
        for assignment in assignments:
            assignment.annotate_with_array(roledefarray, gobarray)
        return assignments