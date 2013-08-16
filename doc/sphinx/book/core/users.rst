User Model
==========


The User model is a key object in the system, and has been implemented by all CMS systems and most web frameworks.

The MEWLO approach will be to keep the user model table itself as minimal as possible, and use helper objects/tables for as much as possible.

Core User model fields:

    * ID
    * Username
    * Email Address: I'm still slightly on the fence about whether we should actually have this as a field in the user model, or whether we might use a separate table for this -- see below.
    * Name
    * IsEnabled

Should Email Address be a field on a user object?  In all frameworks/cms i've seen, email address is a field of the User object.  But this falls into the category of things that can add some inconsistency to the system when we envision cases where a user might specify multiple emails.  In the case of multiple emails, it might still make sense to think of a PRIMARY email (attached to user object) and then SECONDARY emails which are treated completely differently.

I think one could make a reasonable case that the User model object should contain only unique simple fields that we need to access constantly, and move nearly everything else to secondary tables/models.


Another issue to resolve is the extent to which we want to use a parent "Mobject" class to derive from that has a variety of common fields like (IsEnabled,IsDeleted,IsBlacklisted), etc. And which can be referred to by other objects (Log, ACL, etc.).