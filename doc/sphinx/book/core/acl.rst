Access Control System (ACL)
===========================


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

    Managing ACL role definitions (e.g. "A moderator role allows a person to perform these actions on a group")
    Managing ACL relationships (e.g. "The superuser role includes the moderator role")
    Managing ACL assignments (e.g. "This user has the moderator role on this group")
    Providing support backend and GUI functions for the above as well as general



The ACL system is defined by two main models:

AclItems:

    An AclItem defines a role or permission.  It has a name/label and long description.
    For efficiency, it is important that AclItems be hierarchically organized and groups.  Therefore the role of forum "moderator" is defined by an AclItem which has many dozens of AclItem permissions as children underneath it.  Assigning the role of "moderator" to a user gives that user all children permissions.
    So each AclItem should link to all of it's children AclItems.
    Note importantly that we use Acltems interchangeably both for "permissions" and for "roles", and plan to use them to manage group MEMBERSHIPS.  That is, to record that User X is a member of group Y (or the OWNER of group Y), we will use an AclItem/AclAssignment.
    Because we may add arbitrary contextual objects (groups, projects, etc.) the CONTEXT object must be able to reference any object.
    We might also allow some arbitrary properties associated with an item.


AclAssignments:

    An AclAssignment is the actual assignment of a role/permission (AclItem) to an entity.  So we might assign a specific AclItem to a specific User.
    An AclAssignment is not always a simple case of saying that User X has Permission (AclItem) Y.  Often we want to restrict the permission to a specific *context*.  So an AclAssignment can specify an optional context Object, to express things like "User X has Role (AclItem) Y in Project Z".
    An AclAssignment may also be made to a Group as well as a User.  So that if we have a Group we call "site administrators", then we might say that "GROUP X has Permission Y", meaning that all users in GROUP X have that permission.
    We might also allow some arbitrary properties associated with an assignment.