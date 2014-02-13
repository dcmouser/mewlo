Site Configuration
==================

The general approach taken to configuration in Mewlo is that it should be done by standard python code.

That is, we do not have an elaborate confguration/settings "language" (DSL) for expressing settings.  Instead, most settings are configured via object instantiation or standard python dictionaries.

The result is sometimes a longer more verbose configuration/setting section.  The advantage is that we are not introducing another layer of complexity and indirection requiring constant maintenance.



Host-specific and Commandline-switchable Configurations
-------------------------------------------------------

A web site/service is normally designed to run at one specific domain name, and designed to be deployed on one "official" server.
However, it is also common to need to test or develop the site on different computers.
In addition, we sometimes want to make our code available to others (such as on a public version control system).
We also occasionally want to switch between some subset of configuration options.
Lastly, we may be writing code for a site that we expect people to be able to download and customize for their own use.

Because of these scenarios, we need a way for people to easily and safely store and switch between multiple configuration settings for their use.

Here are some requirements we have:

    * Alternate configuration settings (for example for different hosts) should be stored in different files that could be maintained by different people and excluded from some distributions.
    * We will often want a fallback to a default value for some settings, so we want a system that can let us specify defaults and overide as needed.
    * We want to be able to easily mark configuration files as to-be-ignored by a version control system or zip packager; in this way we can put these sensitive configuration options, like database or mailserver passwords, in isolated files.
    * It needs to be easy to specify different configuration options and easily switch between them via commandline option.

So, note that there are two primary issues:

    * We want to help developers keep sensitive configuration information isolated for easy exclusion.
    * We want to help developers keep host-specific and use-specific configuration information modular for easy switching.


Mewlo implements the following strategy and conventions:

    * The MewloSite object has a MCfgModule class object that provides an api for accessing configuration values/objects/attributes that are stored in external files.
    * The normal programatic site configuration can at any time query this object for a configuration value/object/attribute.
    * For example, a call would like like: self.get_configval('mail_smtp_password','GENERIC_DEFAULT_VALUE'),
    * When this call is invoked, the MCfgModule class will return a value for the attribute 'mail_smtp_password' (or the specified default value if not found) by looking for it in an ordered list of modules.
    * The key is that this 'ordered list of modules' is based on a configname parameter, which may be set on the commandline (via option --configname) or programatically at startup.
    * If the configname is 'myconfig' and the site configuraiton directory is set as ".\config"  then the MCfgModule will look for the requested attribute(symbol) 'mail_smtp_password' first in the file '.\config\myconfig_secret.py' and if not found then in '.\config\myconfig.py' and then if not found in '.\config\default.py'.
    * In this way, a configname (which can be set on commandline) defines a precedence of files to check for the symbol, always falling back on default.py (and then finally on a function-passed default if not found in any file).
    * By convention, the configname_secret.py file should only have attributes that one does not want committed to a version control system or shared.
    * By default, all such *_secret.py files are marked to be ignored in .gitignore.
    * Note that these configuration .py files are full normal python module file (rather than some custom config language).  Attributes can be of any type.
    * Note that each module on the precedence listed is imported once and only once at startup of site (rather than on demand as each attribute is looked up).



