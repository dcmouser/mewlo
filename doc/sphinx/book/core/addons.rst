Addons
======


In Mewlo, there are two levels at which addons/plugins/extensions/modules are defined.


First Level
------------

The first operates at the level of groups of files.  This level is handled through MewloPackage class (described in its own section).

A MewloPackage represents one or more files that are distributed as a downloadable package, maintained by a single entity who is reponsible for releasing updates.

A package may contain multiple components, create multiple database tables, etc.

In fact the entire core of Mewlo code is managed by a single "core" package.

It is packages that are enabled or disabled from an administrative section, and are checked for updates online, and are responsible for performing database updates.

Packages my have dependencies with one another.

It is at the package level that we have an API for returning information about the package/plugin author, version, etc., for updating, enabled, disabling.  However the package API does not get invoked or signaled on normal operation of the website.  That is left for objects that register with Mewlo, as described below.

A package will have a section in the administration center and/or in configuration options that allows administrator to change options.


Second Level
-------------

The second level involves objects that actually interact with a Mewlo website.  This may be by registering as listeners to signals/events and reacting to them, or by emiting signals, or by making available services that can be invoked by other code.

These objects and services are registered by the packages when the packages are enabled/loaded.

These objects don't have an api for providing info like version, author, etc.



Using SetupTools Eggs and Entrypoints
--------------------------------------

The Python SetupTools modules have established a general-purpose way for applications to advertise and discover plugins, using a facility known as "entry points" in EGG packages.

The advantages of using the SetupTools entry point system include:

   * It's a standardized approach that is used in many projects.
   * It allows for auto-discovery of plugins that can be installed through standard python install tools like easy setup, pip, etc., even when these plugins are installed outside of the Mewlo directory.
   * Because it works through SetupTools, it provides complex functionality for auto downloading, installing, dependency installation, repository publishing, etc.

The disadvantages include:

   * Overly complex API, and yet insufficient API for accessing meta info about plugins.
   * Overly invasive process needed to install a plugin (i.e. it has to install into your main python site packages).
   * Overly complex requirements for building and testing plugins (they have to be built and installed as egg packages)
   * Duplicative information specified in Eggs
   * Future language-neutrality is harmed by depending on python-specific plugin framework.

Mewlo takes a hybrid approach:

   * Mewlo uses it's own plugin class hierarchy and internal plugin discovery system.
   * Mewlo's internal plugin discovery/loading system depends on human-readable json info files that describe arbitrary information about "plugin" (addon/extension) packages.
   * Mewlo's internal plugin discovery system will autoscan specified directories to discover addon packages -- these can be isolated per site or installation, and require no modifications of system-wide python installation.
   * BUT, Mewlo also knows how to discover python SetupTools based advertised plugins; any found are used to extend the locations that Mewlo looks for it's special addon package info files.
   * In this way, we get the benefits of being able to use SetupTools based plugin discovery, but only for the purposes of advertising/exposing our standard addon package information system.
   * Additionally, Mewlo provides some helper functions that make it easy to create an egg Setup.py file/function that uses meta information from a mewlo addon package .json info files, to eliminate the need to duplicate meta data when creating Egg distributions for a plugin.


See also:
    * http://ziade.org/2010/07/25/plugins-system-thoughts-for-an-entry-points-replacement/