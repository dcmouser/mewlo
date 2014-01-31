Ugly Code
=========


8/12/13:
    * We aren't currently using python eggs and officially installable packages for different components


8/13/13:
    * We are still throwing some exceptions in mcontroller and helpers/callables modules.


8/15/13:
    * The event creation shortcut functions (see bottom of event.py) should use args,kargs to be simpler.


8/15/13:
    * We need to put in place something to check for python3 compatibility.


8/15/13:
    * Our debug function output is ugly -- especially the indentstr parts.  What about returning debug information as a hierarchical list of strings, for rendering in dif ways (including an accordian tree if online).


9/24/13:
    * Routemanager (and log system) uses the startup function to walk a hierarchy of objects and set parenting hierarchy info; this is done so that we can track the hierarchy no matter what order the objects are created. Is there a better way to do this?


9/27/13:
    * We have objects called MewloPackages -- might be too confusing with python term of "packages"; can we rename it to something similar like "packs"?


10/1/13:
    * If you look in misc.py you will see some functions that return Events for exceptions and some functions that raise exceptions.
    * We need a systematic explanation of when/why some functions catch exceptions and return them as events vs those which pass exceptions up the chain and a systematic documentation to make this clear for any given function at a glance.


10/1/13:
    * Take a look at a file like pack.py; note that its impossible to distinguish between api functions meant to be called by someone, vs helper functions used by these.
    * Move all "internal" functions to _ prefixes?
    * By internal i mean functions not meant to be called from outside the class
    * Method functions that are *ONLY* called by other functions within the class, and never called from outside the class should be _ prefixed.


10/9/13:
    * Do we want to make our internal logging system more like python built-in logging system?
    * Or even rewrite ours to use the built in one for most work?


10/10/13:
    * Right now we have a single global signal dispatcher.
    * Receivers register for messages with it, and can set filters on what they get signaled about
    * But with huge numbers of signals this might be a lot of checking
    * Should we instead have receivers attach to specific sender slots?
    * It's possible that we could emulate the efficiency of this using a hash system in the single global dispatcher


10/13/13:
    * Refactor the settings class so that we dont need to INTERCEPT/OVERRIDE normal settings functions, but use pre/post op functions


10/31/13:
    * The sqlalchemy column creation stuff is still awkward.
    * We need a better workflow that will allow us to dynamically add relations and columns to models
    * Sql alchemy stuff is done in a way that makes it hard to refer to sql alchemy columns
    * Move all/most sqlalchemy to declarative style?



1/16/14:

    * There are currently some class-level variables in the MewloDbModel class hierarchy that keep track of things like sqlalchemy tables/relations, etc.
    * when running things like unit tests which build a site multiple times, this requires some kludgey ugly resetting of this data between creations.
    * Too many imports in testsite1.py

1/17/14:

    * The database backed settings class (mdbsettings) is a litle bit ugly
    * The msettings class is a big ugly (especially all the constant setting names)

1/17/14:
    * Eventlist in mevent.py -- let's derive this from a true list

1/20/14:
    * I'd really like to remove all of this stuff where we are passing eventlists to functions for collecting warnings, etc.  There has to be a better way.

1/21/14:
    * We have a problem with the workflow for checking pack updates and specifically critical web update checking, and pack initialization.
    * As it is, we discover packs, load their code, all at startup, and only then can we check for web/database updates.
    * And we cannot check for database updates UNTIL we have loaded the pack objects.
    * What should? workflow look like? 1. discover packs, 2. do web update checks, 3. load code objects, 4. do database update check, 5. enable 
    * Current workflow: 1. discover packs, 2. load code objects + do database update checks, and enable, 3. do web update checks and database update checks

1/21/14
    * I dont think we can support multiple sites if we are using sqlalchemy. think about the fact that model classes are being instrumented, and thus cannot be shared across multiple different tables for different sites.
    * See my help document on managers for a way we could (by using managers to create model objects, they could dynamically create site-specific-derived classes on the fly).
    * However, i think the idea of multiple independent sites being run by a site manager was probably misplaced -- we dont really need to be able to do this do we?
    * Might we instead consider the django idea of supporting multiple sites THAT SHARE THE SAME DATABASE objects.



