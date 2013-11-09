RBAC (Role Based Access Control)
================================


Probably the best example of complex access control requirements can be seen in modern forum systems.
There you can see the need to inherit large numbers of permissions and roles, whose structure may be organized hierarchically, and then (partially) inherited across sections.

The "programming school" also demonstrates how we sometimes need to dynamically create and manage a large set of per-user permissions that are updated frequently, and perhaps automatically -- or managed by different users.  That is, imagine 100 sections with 2 "teachers" in each section, and each teacher can control visibility permissions for users IN THEIR SECTION.

You can also see from complex forum permission assignments (and CMS assignments) how difficult it can be to track and maintain permissions.

I'm not sure there is a great solution to making it easy to maintain permissions.  Perhaps good searching abilities would help

One feature found on forum ACL configuration seems to be the idea of templates -- where you can define a set of permissions that can be applied en masse to a new object.

Another complicating factor is that group permissions can be INHERITED by users, creating a chain of permission settings.  This can mean that we have a hierarchy of permission grants and blocks that override earlier inheritance.. Can get quite tricky and messy.

Yet another complication is for things like projects and user-run groups where we want to give group owners (normal untrusted users) the ability to assign some set of permissions/roles on some group objects as well as perform some kinds of ownership-transfers.

Efficiency is also a serious concern for ACL stuff, and may require some clever caching, because ACL assignments can be recursive and hierarchical and may need to be accessed on nearly every request.

We can think of an ACL system from a few different standpoints:

    * Managing ACL role definitions (e.g. "A moderator role allows a person to perform these actions on a group")
    * Managing ACL relationships (e.g. "The superuser role includes the moderator role")
    * Managing ACL assignments (e.g. "This user has the moderator role on this group")
    * Providing support backend and GUI functions for the above as well as general



The ACL system is defined by two main models:

AclItems:

    * An AclItem defines a role or permission.  It has a name/label and long description.
    * For efficiency, it is important that AclItems be hierarchically organized and groups.  Therefore the role of forum "moderator" is defined by an AclItem which has many dozens of AclItem permissions as children underneath it.  Assigning the role of "moderator" to a user gives that user all children permissions.
    * So each AclItem should link to all of it's children AclItems.
    * Note importantly that we use Acltems interchangeably both for "permissions" and for "roles", and plan to use them to manage group MEMBERSHIPS.  That is, to record that User X is a member of group Y (or the OWNER of group Y), we will use an AclItem/AclAssignment.
    * Because we may add arbitrary contextual objects (groups, projects, etc.) the CONTEXT object must be able to reference any object.
    * We might also allow some arbitrary properties associated with an item.


AclAssignments:

    * An AclAssignment is the actual assignment of a role/permission (AclItem) to an entity.  So we might assign a specific AclItem to a specific User.
    * An AclAssignment is not always a simple case of saying that User X has Permission (AclItem) Y.  Often we want to restrict the permission to a specific *context*.  So an AclAssignment can specify an optional context Object, to express things like "User X has Role (AclItem) Y in Project Z".
    * An AclAssignment may also be made to a Group as well as a User.  So that if we have a Group we call "site administrators", then we might say that "GROUP X has Permission Y", meaning that all users in GROUP X have that permission.
    * We might also allow some arbitrary properties associated with an assignment.



Roles vs. Groups:

There is some potential for confusion when thinking about how to use roles and groups.  An example:

Imagine we are building a forum system.  We create a large number of low-level roles/permissions -- things like: "can edit own post", "can delete posts", "can read posts", etc.
It's clear that that these items are low-level primitive roles.  But now we want to have the concept of a forum "moderator", and we will have a big set of permissions that we are going to assign to all moderators.
It would be far to error-prone to individually assign each low-level permission/role to each moderator.
So instead we will want to organize a bunch of roles/permissions under one heading.
One can imagine several ways of doing this:

    * Create a USER GROUP and assign the collection of roles/permissions to this GROUP.  Then place moderator USERS in this GROUP, and ask that members inherit the roles of the group.
    * Create a higher level ROLE called "moderator-role" that includes the lower level roles as implied children.  Then assign this high-level ROLE to USERS who are moderators.

Which approach is best?  What are the tradeoffs?

The first observation we make is that in the specific simple case above, there doesn't seem to be much of a reason to prefer one approach over the other.  In one, groups inherit roles, in the other, roles can inherit/imply other roles.

However, what if we simply wanted to set up a few simple higher-level roles, that inherited other roles.  For example "edit all posts" might inherit "edit own post".  Without role-inheritance, this would mean creating many overlapping "user groups" with minor permissions.  And possibly assigning users to multiple overlapping "groups" to combine permissions.

In addition, using USER GROUPS to handle permission inheritance seems to be quite different from the use of USER GROUPS that people could join for the purposes of self-organizing, etc.  This confusion is something we would like to avoid [we could of course use different structures for permission-based-user-groups and self-organizing-user-groups if we wanted].

Given these observations, our first decision is that we will prefer to use a hierarchy of high-level Roles/Permissions that can inherit groups of lower-level roles.  This explicitly solves our example problem above.

But now we must still ask the question -- do we still need to support the complexity of group-based inheritance of roles/permissions, or can we do away with this idea and keep things simpler?

Put another way, what does it mean when we say that "GROUP G has ROLE R" or that "USER U has role S in GROUP H"?

This last case bears emphasizing -- our User Group system supports more than the concept of a user being a MEMBER of a group.  Instead we say that a user has a specific "ROLE" in a group.  So some users might be ordinary "members" of a group, while others may be "moderators" of a group, and others may be "owners" of a group, etc.

An example of an easy and common case would be: We want to know if a user can send a message to a group, so we ask "does user U have role R in group G" -- only if they have a role IN GROUP G that includes the permission to send messages will we let them.

But things get more complicated if we allow for HIERARCHIES OF USER GROUPS.

In this case, if group H is a child of group G.  And user U is a moderator on group G -- what do we say about user U's roles on the child group H?  Do some roles get inherited by child groups, and others not? How would we express such things?



An alternative to Multiple Tables:

Instead of having different tables for different Subject and Object combinations (for example a table for expressing "USER U has ROLE R on GROUP G" and a separate table for "USER U has ROLE R on DOCUMENT D", we could instead use a unique RESOURCEID.

Then we have a SINGLE role assignment table mapping "RESOURCE S has ROLE R on RESOURCE T".

And where *EVERY* object in the system has a GLOBALLY UNIQUE RESOURCEID, assigned at time of its creation.

Then we need only a single table for role assignments.

What are the downsides:

    * We need to ensure object has a unique RESOURCE ID, at time of creation -- this seems a little hairy.
    * We may need to perform multiple lookups to check permissions (for example if we want to know if user U has permission on Group G" we have to first determine the RESOURCEID for the user and the group, before doing the permission lookup.  With the separate table approach we do not.
    * Reverse mapping from role assignments to objects is a bit trickier.  With separate table we know our left+right sides map to specific object types.  New method requires a reverse lookup on a specific Resource ID table without the possibility of foreign keys.
    * Related to above, separate tables lets us use a nice ORM on our role objects.
    * We may lose some efficiency that we could get by being able to cache certain common role tables; though using a single role table might allow different optimization/caching.

Upsides:

    * Cleaner to have only one single resource table.
    * Having every object possess a globally unique RESOURCEID, could come in VERY HANDY for other operations like logging.  This is the most compelling argument for this approach to me.
    * Some queries can now be done (at least initially) by querying the sole role assignment table.  For example if we want to know ALL permissions related to user U, we can now do this in one query of the role assignment table (though we would then have to do followup queries to get specific target info); with multiple tables we would have to query each table that related to USER.

Other observations:

    * While generating a globally unique RESOURCEID for every object is a bit painful, it only has to be done at time of object creation, which is infrequent.
    * Most of the time, we will already have loaded the information for an object (user, group, resource), so the globally unique id may already be in memory and not require a separate lookup.  For example if the logged in user is trying to do something in group G, we will certainly already know the user's globally unique resource id.
    * To keep database tables "normalized" we could have each object keep a foreignkey to the primaryid in a RESOURCE table, and *NOT* link back from resource table to source object (but store a string in the resource row saying the name of the object TABLE so we could reverse-lookup if we wanted to given the resourceid).

To me, the key motivation for using a globally unique resource ID is simply that it could be useful in other cases besides the permission system.  And if we assume every object has a unique RESOURCE id, then using it for ACL seems natural.


