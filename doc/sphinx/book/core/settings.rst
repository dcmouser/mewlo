Settings Registry
=================


The Settings Registry is a (usually) global API that provides easy access to a global registry of hierarchical settings.

We will have both a global persistent registry (cached within a request), as well as a per-session/thread transient "registry" which is really just a thread-local dictionary.

The global persistent registry would normally be stored within a database, *BUT* there may be some settings that we want to configure EARLY from within configuration files (for example database connection parameters).  It would be nice to expose both db settable values and early config file settings from a unified API.  A logical approach would be to have the config file settings load early, and be used as defaults unless overridden by database settings.  Alternatively, and maybe more safely, we could say that an error will throw if any attempt is made to set via database an option set in file configuration.

    * Some useful functions in our Settings Registry API might include:
    * Tracking of changes
    * Alerting of admin when certain values are changes
    * Ability to protect certain settings.
    * Ability to access hierarchical data via dot notation.


Different places that settings might be set/loaded:

    * Manually created hierarchical dictionary specified in site-specific early configuration file(s); e.g. to specify database connectivity information.
    * Database-stored site configuration data, available after database connectivity established.
    * Loaded as default settings from various plugin files.
    * We may have multiple places where settings conflict, because some are defaults and some are meant to override these defaults.