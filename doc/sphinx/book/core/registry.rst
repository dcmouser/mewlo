Component Registry
==================


The MewloComponentRegistry provides a way for objects and services to "register" themselves with the Mewlo system, and make it possible for other parts of the system to find them.

This is similar in spirit to the Zope Component Architecture (http://bluebream.zope.org/doc/1.0/manual/componentarchitecture.html), but much simpler.

In essence we simply provide a way to register an object with the registry, and specify the features it provides (via a simple dictionary).

Other components can query the registry and ask for a list of components matching certain features.

In this sense, most of what the registry system does is by "convention".  That is, we expect the users of the registry to agree on feature keywords and values in order to find each other.

We will need to keep a published list of such keys used.

We can contrast this approach to the Zope Component Architecture approach which uses a much stricter system of type checking interfaces and class hierarchies.

While such an approach does a better job of catching errors early, and is generally a more pure OOP strategy, we have chosen in the case of plugins/addons/packs to favor a simple generic communication/interfacing protocol.
Our experience has been that while a strong typechecking approach is useful for internal code, the nature of addon development and constantly changing APIs, and the complexity in creating compliant small addons, make the looser generic approach a better solution.


See also:

   * The Mewlo Signal Dispatcher system.