Site Addons
===========

Django has the concept of an "App" which is a moduler, reusable, self-contained set of files that implement some controller routes, views, and configuration information.
Think of an "App" like a self-contained add-on which can handle certain requests (usually matching a url prefix).

The reusable and modular nature of such bundles is what makes them appealing.

Mewlo supports such a concept.  The term "app" is misleading but i don't have a much better term at this point, so i'm just refering to them as "site addons".


Django docs on how these "apps" are self-contained:
    * https://docs.djangoproject.com/en/dev/intro/reusable-apps/ - general
    * https://docs.djangoproject.com/en/dev/ref/templates/api/#template-loaders - template treatment
    * https://docs.djangoproject.com/en/dev/intro/tutorial06/ - static file treatment
    * http://www.caktusgroup.com/blog/2013/06/12/making-your-django-app-more-pluggable/
    
    

Mewlo SiteAddon Structure
-------------------------

A site addon gets its own directory under the site_addons\ subdirectory.
There it will have some files:

The first two files are "mpack"-related files; this is our system for organizing code into "mpacks" which have version+author info and can check for updates, etc.
All code in Mewlo MUST fall under the jurisdiction of an mpack (be that the core mpack or another).
Usually each siteaddon has it's own mpack that organizes it, but it is permissable to have multiple siteaddons contained in one mpack.
These two mpack files are basically standalone files -- they don't need to interact in any other way with the siteaddon code, they are just there to define the collection.

    * msiteaddon_NAME_mpack.json - describes the site addon author, version, etc.
    * msiteaddon_NAME_mpack.py - the associated mpack that contains a MewloPackWorker-derived class

Now we get to the actual files doing work.

By convention, the one required file for a siteaddon will be:

    * msiteaddon_NAME.py - this file will define a class derived from msiteaddon.MewloSiteAddon.  This class will contain functions for setting up routes, aliases, navnodes, etc.
    * msiteaddon_NAME_manager.py - this is an optional file that will be found in most siteaddons -- it defines a class derived from manager.MewloManager which will be attached to the site and contains functions triggerd by requests/routes and other helper functions.
    
By convension, a siteaddon directory contains subdirectories organizing other files for the site addon:

    * controllers/ - used if we want to put control functions in separate files instead of a manager.
    * forms/ - form class files we might use
    * staticfiles/ - any static resource files used/served by the siteaddon
    * views/ - any view files used by the siteaddon


