Site Components
===============


The help section on [extending] mewlo discusses some of the motivation and design principles for mewlo that are focused on making it extensible.

One extremely simple mechanism for facilitating extensible design in mewlo involves registering objects with the site as "Site Components".

A Site Component is simply an instantiated object that implements a minimal API for startup and shutdown functions, and which registers itself with the Site object at construction time.

The main point of using a Site Component object is that it can be looked up by name by other code, and can be REPLACED by duck-typed alternative objects at runtime.

That is combined with the important programming convention that code should avoid at all times the reference to specific hardcoded CLASS names.  Instead, all substantial work should be done by Site Components which are looked up by name.

For example, if we want to create a new user object in a custom module we are writing, we do not use code like:
  user = MewloUser()
Instead we use something like:
  user = site.comp('sitemanager').create_user()

Although more verbose, this code means that we can easily swap in a replacement derived User class non-invasively without changing our code.



