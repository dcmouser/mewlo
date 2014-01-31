Packages / Extensions
=====================


Every part of Mewlo, including the built-in essential Core components as well as 3rd party plugins/addons and should be arranged in terms of "Packages".

In that sense, not every pack is a "plugin".
And multiple "plugins" might be managed by a single downloadable "pack".

Perhaps the best way to think of a pack is as a collection of code that is treated as a "unit" for the purposes of updating and version control.  Update checks are performed per-pack, and database updates are performed by the packs.

A Package should always be a single self contained directory branch (it can have subdirectories).

A Package needs to implement an API that provides the following:

    * Information about the module that can be displayed on a configuration page.
    * Information about any dependencies with other modules or libraries.
    * Configuration pages made available to the system administrator.
    * Version information and update checking url so system can check for updates.
    * Functions to create initial database tables for any models/tables managed by the Package.
    * Functionality to check database table versions, and UPDATING/CHANGING tables when versions change if necessary.
    * Functionality for exposing tests that can be run from admin backend.
    * Functionality for backing up tables before updating.

Descriptive information about the pack needs to be available even when module is disabled.

Can we auto download updates to packs, and auto install?

We would like as much as possible of the CORE of Mewlo to be built as "Packages", because that gives us a unified approach to update checking, version reporting, database updating, etc.  That might mean that Mewlo has only a "micro" core that is not a Package.

There will be 3 places where packs may be installed:

    * mewlo/mpacks/core - the base core required packs that power Mewlo (required and non-optional)
    * mewlo/mpacks/user - any user-installed optional packs that are available for ALL Mewlo sites using this Mewlo install.
    * SpecificSite/packs/user - any user-installed optional packs that are localized for this one site application.


Example of a good lightweight python plugin system: http://yapsy.sourceforge.net/


Mewlo can check for updates to packs online.
Should Mewlo include it's own downloader and pack installer?  To what extent should it interoperate or depend on standard "pack managers"?

Packages may perform database updates, and installation and uninstallation procedures.