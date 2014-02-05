Site Configuration
==================

The approach taken to configuration in Mewlo is that it should be done by standard python code.

That is, we do not have an elaborate confguration/settings "language" (DSL) for expressing settings.  Instead, most settings are configured via object instantiation or standard python dictionaries.

The result is sometimes a longer more verbose configuration/setting section.  The advantage is that we are not introducing another layer of complexity and indirection requiring constant maintenance.



Host-specific Configuration
---------------------------

A web site/service is normally designed to run at one specific domain name, and designed to be deployed on one "official" server.
However, it is also common to need to test or develop the site on different computers.
In addition, we sometimes want to make our code available to others (such as on a public version control system).
Lastly, we may be writing code for a site that we expect people to be able to download and customize for their own use.

Because of these scenarios, we need a way for people to specify custom configuration settings for their use.

Here are some requirements we have:

    * Configuration options for different hosts should be in different files that could be maintained by different people and excluded from some distributions.
    * We will often want a fallback to a default value for a setting.
    * We want to be able to easily mark host configuration files as to-be-ignored by a version control system or zip packager.
    * It needs to be easy to specify different configuration options for different hosts and easily switch between them via commandline option.


So, note that there are two primary issues:

    * We want to help developers keep sensitive configuration information isolated for easy exclusion.
    * We want to help developers keep host-specific configuration information modular for easy switching.


Our strategy is as follows:

    * The MewloSite object will have a host variable, which can be set in the config, but will be overriden by a commandline option. 
    * We supply a helper function for MewloSite class, that can be called to lookup a host-specific attribute (variable value, etc.).
    * This function will try to look up such values, using the first matching attribute found when checking the following, IN ORDER:  [hostname]_secret.py, [hostname].py, default.py
