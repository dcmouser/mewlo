Managers
========

Although the current codebase (1/30/14) does not conform to this approach completely, ultimately Mewlo should use instantiated singleton-like Manager objects to liason with specific MewloDbModels (database object models).

So, for example, we might normally be inclined to do:

	newuser = MewloUser()
	newuser.save()

Or, if using class methods, something like:

  newuser = MewloUser.make_new_user()
  newuser.save()

We advocate something like this:

  newuser = site.comp('usermanager').make_new_user()
  newuser.save()

Or, equivelantly:

  newuser = site.usermanager.make_new_user()
  newuser.save()


Why?
----

One major reason to do that is that it creates a layer of abstraction regarding the MewloUser class, and removes the need to hardcode the database object class types.

So for example, if the programmer wanted to, they could with one line drop in a REPLACEMENT 'usermanager' component which used a different ducktyped/derived class based on MewloUser.

Another reason is that the manager objects are PERSISTENT.  They may cache data and they are cleanly retrievable by name from the site object.  It is more natural for them to interface with multiple kinds of models.

Part of the motivtion for letting (model) managers do most of the heavy lifting, has come from the awkwardness and confusion that comes from trying to put such code in model classes themselves.  The division of labor helps separate simple functions that can operate entirely within the lightweight model object (accessors, etc.), and more elaborate functions which may involve interfacing with other models and site objects -- which is handled by a manager.
