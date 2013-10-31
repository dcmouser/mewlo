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


Let's think about the different ways/places we can store a user profile piece of information.

    * In the core (built-in) user table, with a dedicated column.
    * In a dedicated column in a separate table (for example an extension/addon table).
    * In the core user table, but serialized in the generic extra data large-text column.
    * In a special (user-specific, generic, or extension) table made up of key-value pairs.   AKA the Entity-Attribute-Value (EAV) model.
    * We could drop the use of sql-rdbms comletely and go with a nosql like mongodb.


Issues to think about when contemplating these options:

    * To what extent is the field efficiently searchable?
    * How much programmatic effort and database resources are required to save/load the value(s), and can we easily do lazy loading of it?
    * To what extent is the approach shareable for many different kinds of objects not just users?
    * What kind of help can sql alchemy give us for this stuff?
    * To what extent can we hide the implementation choice from the api?
    * To what extent can we make it easy to change the backend implementation?


And how do these options break down?

    * Storing in a serialized array is for all intents and purposes UN-searchable at any cost.
    * Storing in a serialized array becomes very cheap as an amortized cost if we have lots of data for a given user (e.g. one textfield read vs 20).
    * Storing in a key-value table does support searching, though considerably more costly (requires left join) when combining with other fields.
    * Storing in a key-value table can be problematic in terms of space or efficiency or programmatic complexity because of column type issues (e.g. do we have to use large-text field to handle worst case needs for any given property).
    * Storing in a key-value table makes it a single query to retrieve all data for a user.
    * Storing in a key-value table is very efficient for rare fields that dont apply to all users/objects.
    * Storing in a dedicated column is standard normalized approach.
    * Storing in a dedicated column in different tables can result in some elaborate database joins and multiple queries fto get fields from different tables.
    * A non-sql database (like mongo db) would be well suited for this kind of data.
    * The most efficient thing for most fields is a dedicated column, in the main user table.
    * Letting addons add to the main user table is messy and harder to maintain safely.


Let's see if we can't cull some choices:

    * Our desire for clean maintenance, we will forbid extensions/addons from adding columns to the main user table.
    * Because at least some addon fields will require searchability, we can eliminate the use of serialized field data (at last as the ONLY solution).
    * Again for clean maintenance, we would like addons/extensions to be able to manage their own profile addon data for users (etc.).
    * SO, we *KNOW* that one approach we will want to support is have user profile data spread out over multiple tables (managed by other modules and expanded).
    * That leaves us with our final issue.  There are going to be profile fields that are generated dynamically and fluidly, for which creating columns for is probably not practical.
    * In such cases, should we use key-value pairs or a serialized array?


See:

    * http://www.dbforums.com/database-concepts-design/1619660-otlt-eav-design-why-do-people-hate.html
    * http://weblogs.sqlteam.com/davidm/articles/12117.aspx
    * http://tonyandrews.blogspot.com/2004/10/otlt-and-eav-two-big-design-mistakes.html
    * http://stackoverflow.com/questions/7933596/django-dynamic-model-fields


Strategy:

    * I like the idea of making the API hide the implementation, and could even be used with a nonsql.
    * Use properties help mixin.


How do we want to represent anonymous users?