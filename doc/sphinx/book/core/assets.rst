Working with Asset Files
========================

Asset files refer to any static files (view template files, css, js, image files, etc.)


Issues in Referencing Asset Files
---------------------------------

Perhaps the single most important non-trivial design issue for templates and output generation in general, is how to best facilitate the referencing of "asset" files:

    * We want a uniform concise way of referring to them, which does not require absolute paths to be specified, and makes it easy to move files around.
    * We want addons to be able to contain their own localized isolated asset files (even when such files appear to be elsewhere to the visitor).
    * We want the coder (and other package authors) to be able to selectively replace arbitrary asset files, much like a skin might override default files, non-invasively.
    * We'd like to avoid forcing the user into listing/defining every single asset file.



A Strategy for Referencing Asset Files
----------------------------------------

We adopt the following strategy when it comes to asset files:

    * We use a "global" alias system that holds short, dynamically created aliases to file paths.
    * The aliases provide a way to use dotted path names to refer to package asset directories and files without having to refer to paths.
    * Some items will have both file paths and url paths; in such cases we want a uniform pattern for naming both.
    * There are cases where we want to set a base path within a context; such as a base view path from within a controller, etc.  In such cases we will use a simple alias ${b} to represent this value.
    * To enable users and addons to replace asset files non-invasively, the site alias system will allow for the registering of search and replace patterns in asset paths.  Asset alias resolution will perform these.
    * In this way, single files or entire subdirectories can be dynamically replaced.
    * We may want to support a replacement specification which only affects asset files where the replacement file is actually found.  This would enable a skin-like replacement of a subset of files, as found.


What can you do with Asset Manager
-----------------------------------

Borrowing from pyramid, the asset system can be used to:

    * Refer to a file (or directory) as being relative to a package/alias (rather than by absolute path)
    * Refer to a file/directory as relative to some current context
    * Tell mewlo to make files/directory available as if they were in public html accessible area.
    * In the above case we have multiple options, including asking mewlo to physically copy them (and recopy when they change), or to serve them per request, performing some kind of authentification check.
    * Generate urls for both internal and external links
    * Be smart about whether to use https or http when generating links.
    * Allow users/addons to override/intercept pre-existing assets with replacements
