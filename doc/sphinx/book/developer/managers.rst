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

The single most important reason to do that is that it creates a layer of abstraction regarding the MewloUser class, and removes the need to hardcode the database object class types.

So for example, if the programmer wanted to, they could with one line drop in a REPLACEMENT 'usermanager' component which used a different ducktyped/derived class based on MewloUser.

