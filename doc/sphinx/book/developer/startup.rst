Component Startup
=================

Startup of mewlo components is not a simple thing, because components have have convoluted inter-dependencies on one another.
These inter-dependencies are further complicated because some components may be created by other components (for example plugins that are instantiated by a pluginmanager component).

We would like to treat all components in a single standard generic fashion with regards to startup.