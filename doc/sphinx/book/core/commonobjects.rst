Common Mewlo Object Stuff
=========================


Some common object stuff to think about:

    * Multiple versioning info (storing older copies of objects)
    * Creation/modification information (timestamps of last modification and author/ip of modifier, and of creator)
    * Policy and mechanism for handling "virtual" deletions, drafts, approval workflows, etc.
    * Need to support dynamically added attributes with lazy load/save
    * Need to support extension-added attributes with lazy load/save
    * Support for ACL rules



Some strategies follow
-----------------------


Generic Versioning Table:

We will take a low-tech approach to generic versioning support, as follows:

    * We will use an EAV-style approach to versioning, using a generic version table with fields for: ObjectType, Timestamp, AuthorId, AuthorIp, Serialized Data
    * We expect this to be a mostly write-centric database; for wiki-heavy objects a custom table would be in order.
    * We will provide some extra functionality for auto archiving of old data.

In addition (alternatively):

    * We may also support a function where database model objects support the ability to write out to an alternate archive table.
    * This would be another generic way to support archive copies as well as backup data, and would have the advantage of preserving all normal database table constraints.
    * One downside to this is a proliferation of additional tables (one for each model).
    * The versioned tables need to use the original primary id as their non-unique "reference id", and use their own primary id.


Standardized Fields for creation/modification:

    * CreatorId, CreatorIp, CreationDate
    * LastModificationId, LastModificationsIp, LastModificationDate


Standardized fields for workflow and deletions:

    * IsDeleted	- moderators can "virtually" delete items and they remain in the table but are treated as invisible; all procedures need to check this.
    * IsDraft - author voluntarily uses this to keep the item private and not ready to be published or checked.
    * WorkflowStage - an enum that is used to track an object through various stages before publication; typically this will be used when objects need approval from a moderator, group leaders, etc.


Supporting the addition of new attributes (aka fields, columns, properties):

    * A Mewlo object model will have some defined database fields.
    * These defined fields would be in the main table for the object.
    * In addition, an object may have a collection of PropertySet objects added to it.
    * Each PropertySet is a model object of it's own.  So essentially this is a "has-a" relationship with the main object.
    * This means that for the main object, the PropertySets are lazy load/save, only loaded on request.
    * Addons/extensions would normally add complete PropertySets.
    * I suppose it would be possible for them to splice new fields into an existing PropertySet (or even into a main model).
    * The database API should hide whether such stuff is done via RDBMS table modififications or in fact a nosql thing.
    * When we find/get objects we can ask that some/all propertysets be loaded at the same time.


The ACL System is made up of 3 sub-systems:

    * ACL Definitions - these define things like roles
    * ACL Assignments - these take the form of Subject S has role R on object O
    * ACL Relationships - these define the relationship between ACL roles; they express things like "having role 'member' implies a set of additional sub-roles (permissions)."

A real question is how ACL Assignments refer to objects. One option would be a very generic approach where such objects were referenced by a typename and an id.
This would work but it makes the id column multipurpose and harder to join on.
Another option is to add dedicated fields for the most common objects to use ACL on (namely users and groups).
The other option that *seems* like it would be too messy but which might work well if we use a nice manager class, is to use many dedicated ACL Assignment tables for combinations of Subjects and Objects.
We will be using this last approach.


So let's look at the kind of things we will be querying the API for the ACL Assignment System about:

    * Does user S have role(permission) R on object O? -- this will be the MAIN question we will be asked
    * Does group S have role(premission) R on object O?
    * Does user S have role(permission) R in group O? -- another common question
    * Does user S have role(permission) R? -- another common question
    * Which users have roles in group O?
    * What Roles does user S have in group O?
    * What Roles does user S have on anything? - multitable queries

In the first few cases where we have Subject and Object classes fixed, we will be looking up rows in an ACL assignment table specific for S-O classes.
The problematic case is the last one when we are asking for multiple subject classes and/or multiple object classes.  But this is a rare case.  We rely on the ACL manager to know how to query multiple tables.


We still have a tricky issue to deal with in terms of hierarchical relationships of objects and ACL permissions.
For example, if we ask: "Does User S have role R in group O?" we need to do some hierarchical lookups:

    * We need to find all the roles Ra that INCLUDE role R as a hierarchical child.
    * We have to find all groups Gs that INCLUDE user S as a hierarchical child.
    * We have to find all groups Go that INCLUDE group O as a hierarchical child.
    * And then ask if there are any assignments that match any combination of Gs,Ra,Go or S,Ra,Go

In a more general case where the object of the test is an arbitrary object, we may need to consult multiple tables to find the parent owners of the object (might be a group or other objects).

So in the most general case, we need to be able to ask for any given Subject or Object, for a list of all hierarchical parents that subsume them in ACL role tests.

However there is an additional complication.

When looking for hierarchical user membership in groups, we have to worry about actual group membership roles, e.g. user X is a MODERATOR of group Y vs user X is a member of group Y.


Other important notes:

    * Things like group membership is represented in the ACL assignment system as a role.





