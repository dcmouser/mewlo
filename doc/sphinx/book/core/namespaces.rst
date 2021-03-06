Namespaces
==========

Django uses the concept of url namespaces (https://docs.djangoproject.com/en/dev/topics/http/urls/#url-namespaces-and-included-urlconfs).

A url route maps a pattern to a controller (view) function that gets called when the url pattern is matched.  We sometimes want to refer to a url route BY NAME, for example when generating a url dynamically.

In Django, url namespaces serve of a couple of purposes related to writing modular, reusable, compartmentalized code:

    * With a module (app, addon, etc.), one can refer to urls by name, using short names that *implicitly* use the *current* namespace.
    * Namespaces allow us to use short names without worrying about clashing with other modules (apps).
    * Using namespaces that can be specified/overridden at time of instantiation means that we can dynamically instantiate multiple copies of a module (app, addon, etc.), giving each one a different custom namespace; allowing us to refer to each one specifically.
    
So, there are TWO key ideas as work:
    1. Things (named urls for django), can have namespaces, and we can refer to them by name, either explicitly specifying a namespace, or using the implicit current namespace.
    2. We often want to instantiate multiple copies of some object (or collection of objects), where it will be easy to specify a custom namespace for each, while keeping the object names unchanged.


Mewlo follows this idea and supports route (url) namespaces in a similar fashion.
When a request is matched against a route, the request notes the matching route and inherits that namespace as its current namespace.
Lookups of routes by name are done in that default namespace -- but explicit namespaces provided along with names for lookup can be used when needed.

In addition to url route lookups, Mewlo also has a concept of NavNodes, which are used to build site/menu structure, and which closely relate to url routes by name.  NavNodes are set up with the same namespace system as url routes, and work the same way.

The idea is consistent -- we look up objects by name, with an explicit or implicit namespace helping to resolve lookups.


Namespace use in Views, Templates, and Aliases
----------------------------------------------

In addition to url routes and nav nodes, we use the same namespace system to provide the same functionality to alias lookups -- which have the same demands.  Alias resolution is used in template view lookups, etc. and so this affects all view file lookups.


It's worth noting that this is quite different from the way django does template lookup.  Django uses an ordered list of Template loaders and directories.  When one references a template file, django searches these directories (loaders) and returns the first matching file.  Django does not have a namespace system for such template/file lookups.



Shadowing
---------

In Mewlo, one always specifies a full file path, whether referring to a template file or a static resource file.  But this file path will typically use an alias to refer to a specific directory.  Aliases use the same namespace system as url routes.

One consequence of this difference in looking up template (and other static files) is how the two systems allow a user to REPLACE files provided by other modules.  In Django, any module/app can and will replace template files simply by using files of the same name and registering an earlier template directory (what about static files?).

In Mewlo, such replacement of files (templates or static assets) is done explicitly, by telling mewlo that one directory shadows another.  Any file found in a shadowing directory will overide its shadowed counterpart.  Shadowing works for both template files and any other static assets (and works in conjunction with static asset mounting -- see separate help document).

By default mewlo sets up a shadowing directory under each project for the entire mewlo system -- in this way it's easy for a developer to overide/shadow any static resource or template file.

Note that neither for Django or Mewlo does this functionality make it easy to replace CLASSES/code modules.



Coding Guidelines Relating to Namespaces
----------------------------------------

Functions that take namespace and childid should pass namespace first.
Always use misc.namespacedid(namespace,childid) function to compose a namespaced id.
This function will add :: prefix if namespace is None or '', so it always fully qualifies a name.
This function will use a childid of 'ANONYMOUS' if the childid is blank.
This function will NOT add a namespace:: prefix if the variable already has a namespace (no nesting namespaces).
Namespaces should not use any characters that are unsuitable for file paths, and should avoid the use of _ (since the _ is used in filepaths to separate namespace from childid).





TO DO
-----

We need to think a bit more about multiple instantiation of Mewlo addons/mpacks, since it's not something we have given much thought to thus far.
Can we come up with some examples from django where it is used?

In mewlo, this would work by instantiating mpacks/addons using a different mewlo component name, and a different namespace.