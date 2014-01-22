Mewlo Theme Override System
===========================

Things get complicated when we have core or addon packages which want to provide view files that the user *might* want to replace, or which might be replaced by theme packs.

As an example, consider all of the login/registration type view pages that are part of core mewlo code.

We want a coder to be able to replace these view pages (as well as optionally replace or extend the controller logic, etc.).

How do we let the custom site coder selectively replace view files?

It's not just view files, it's also related asset files like graphics and css files.

So, the general approach we take to solve this is that all filenames related to view/template/asset files will pass through a central function which can be told about any overides.


So for any view/asset file requested, we will look it up to see if there are any overides for it.

We may let overides be specified in a variety of flexible ways.  As long as we have a central choke point through which all such file lookups pass, we have many options.

Such a system would let any module replace (and override and re-replace) arbitrary files.  The manager could allow whole directories to be replaced with one call.

One nice option that could be built on top of this system as convention is the following:  In a custom site directory called "overrides" we can allow a deep directory that mirrors any section under the mewlo directory structure.  In that way one can replace any file simply by placing it in an identically named subdirectory mirroring the mewlo site directory.


There is one complication, and that has to do with absolute filename paths.  In order for this scheme to work, the file paths passed into our overrider function have to be normalized in some sense.
And it's not clear exactly how to normalize such files -- perhaps relative to mewlo root?




Overide Resolution of View/Template/Asset Files
-----------------------------------------------

So there are two kinds of files we need to provide overide support for:
    * Files served up as public static resources embedded in web pages (css files, images), and normally served up through url requests.
    * Internal private files, like view templates, loaded internally.

The second case just requires that we pass all internal filenames through our overrider function before we process them with view loader, etc.

In the first case, we have two choices -- we can either modify URLS with overrides before they are generated, or modify the filenames before serving them.

Modifying the filenames before serving would be the most parsimonious approach and would mean everything is done with one single type of override.

However, it would break the ability to serve static files efficiently using a non-mewlo web server system, and loses any efficiency to be gained from caching web page outputs.