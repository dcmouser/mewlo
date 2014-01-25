Controller Style
================

In Mewlo, as in most MVC-based web frameworks, we typically have a route configuration that matches a url request, which hands off control to a "controller" function (in django these are confusingly called "views").

In Mewlo, the controller functions are normally not class methods -- they are plain vanilla python functions in one or more python files.

In terms of coding style, in Mewlo, these controller functions should be treated like GUI "onclick" type functions -- that is, they should have absolutely MINIMAL code inside them.  Their sole purpose in life should be to invoke code in other classes and functions.

Why? Because we want code to be reusable and DRY.  Invoked controller functions frequently start off as actions only performed through the GUI, only to morph into operations performed in several scenarios -- possibly even scenarios not involving a logged in user.  So all work should be done in separate code only thinly invoked by controller functions.

We recommend the use of helper classes for performing such work.