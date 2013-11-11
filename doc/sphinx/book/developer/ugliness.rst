Ugly Code
=========


8/12/13:
    * We aren't currently using python eggs and officially installable packages for different components


8/13/13:
    * It looks like when dynamically importing modules (ie packages), relative imports are not being supported; this could create hardships.
    * See http://stackoverflow.com/questions/5078590/dynamic-imports-relative-imports-in-python-3
    * I solved this for now by using version3 of the import function in callables.py


8/13/13:
    * We are still throwing some exceptions in mcontroller and helpers/callables modules.


8/15/13:
    * We sometimes use ' and sometimes use " for strings; decide on a standard and explain why and make all consistent.
    * We sometimes use % operator, and sometimes use +; be consistent.  Is % being deprecated?


8/15/13:
    * The event creation shortcut functions (see bottom of event.py) should use args,kargs to be simpler.


8/15/13:
    * We need to put in place something to check for python3 compatibility.


8/15/13:
    * Our debug functions are ugly -- especially the indentstr parts.


9/24/13:
    * Routemanager (and log system) uses the startup function to walk a hierarchy of objects and set parenting hierarchy info; this is done so that we can track the hierarchy no matter what order the objects are created. Is there a better way to do this?


9/27/13:
    * We have objects called MewloPackages -- might be too confusing with python term of "packages"; can we rename it to something similar like "packs"?


10/1/13:
    * If you look in misc.py you will see some functions that return Events for exceptions and some functions that raise exceptions.
    * We need a systematic explanation of when/why some functions catch exceptions and return them as events vs those which pass exceptions up the chain and a systematic documentation to make this clear for any given function at a glance.


10/1/13:
    * Take a look at a file like package.py; note that its impossible to distinguish between api functions meant to be called by someone, vs helper functions used by these.
    * Move all "internal" functions to _ prefixes?
    * By internal i mean functions not meant to be called from outside the class


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
    * Refactor the settings class so that we dont need to INTERCEPT normal settings functions, but use pre/post op functions


10/31/13:
    * The sqlalchemy column creation stuff is still awkward.
    * We need a better workflow that will allow us to dynamically add relations and columns to models


10/31/12:
    * Sql alchemy stuff is done in a way that makes it hard to refer to sql alchemy columns
    * Creation order of tables and relationships is problematic.
    * Move all/most sqlalchemy to declarative style?


11/9/13:
    * The mixin module is weird and inconsistent


11/10/13:
    * Instead of manually calling every "manager" in site startup and shutdown, can we iterate through a list?

