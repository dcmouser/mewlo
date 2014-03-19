Namespaces
==========

Django uses the concept of url namespaces (https://docs.djangoproject.com/en/dev/topics/http/urls/#url-namespaces-and-included-urlconfs).

A url route maps a pattern to a controller (view) function that gets called when the url pattern is matched.  We sometimes want to refer to a url route BY NAME, for example when generating a url dynamically.

In Django, url namespaces serve of a couple of purposes related to writing modular, reusable, compartmentalized code:

    * With a module (app, addon, etc.), one can refer to urls by name, using short names that implicitly use the current namespace.
    * Namespaces allow us to use short names without worrying about clashing with other modules (apps).
    * Using namespaces that can be specified/overridden at time of instantiation means that we can dynamically instantiate multiple copies of a module (app, addon, etc.), giving each one a different custom namespace; allowing us to refer to each one specifically.
    
Mewlo follows this idea and supports route (url) namespaces in a similar fashion.
When a request is matched against a route, the request notes the matching route and inherits that namespace as its current namespace.
Lookups of routes by name are done in that default namespace -- but explicit namespaces provided along with names for lookup can be used when needed.

In addition to url route lookups, Mewlo also has a concept of NavNodes, which are used to build site/menu structure, and which closely relate to url routes by name.  NavNodes are set up with the same namespace system as url routes, and work the same way.

In addition to url routes and nav nodes, we will use the same namespace system to provide the same functionality to alias lookups -- which have the same demands.  Alias resolution is used in template view lookups, etc. and so this affects all view file lookups.


TO DO
-----

We need to think a bit more about multiple instantiation of Mewlo addons/mpacks, since it's not something we have given much thought to thus far.
Can we come up with some examples from dhango where it is used?