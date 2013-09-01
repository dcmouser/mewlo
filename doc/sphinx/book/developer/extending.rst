Extending Mewlo
===============


This page will focus on the approach to allowing the extension and customization of Mewlo-based projects.

There are a number of different kinds of "customization" that one might talk about.

    * Allowing developers to create (library) plugins/addons that ADD extra optional functionality.  These are things that many users might install into their Mewlo system to provide extra features to their site.  They need to have update support, etc.  These could be things like widgets, etc.
    * Allowing people to write localization/translation text for any text output of the system and share such translations, and easily update them.
    * Allowing developers to easily and non-invasively OVERRIDE/REPLACE (core or addon) classes with interface-compatible classes,.
    * Allowing developers to easily and non-invasively OVERRIDE/REPLACE template views, static resources (css, images, etc).
    * Allowing developers to easily group and package addons/customizations/site specific implementations to make maintenance easier.


Design features that would support these:

    * A robust event/signal/slot messaging system to allow plugins/addons to subscribe to and modify and inject and catch events non-invasively.
    * Use of standard unicode translation/localization system.
    * Use of centralized class repository as indirect factory/manager for ALL important class use -- this could be a bit of a pain, and a way for extensions/plugins/addons/site-developers to drop in interface-compatible derived replacement classes and register them non-invasively (or via configuration file).
    * Use of a centralized repository managing all retrieval of static resources / templates, where any addin can overide any resource with a local resource.
    * The previous two items suggest that all classes, resources, etc. should be referred to by ALIAS name rather than by assumed location or class name.
