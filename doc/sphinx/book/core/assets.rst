Working with Asset Files
========================

Asset files refer to any static files (view template files, css, js, image files, etc.)


Issues in Referencing Asset Files
---------------------------------

Perhaps the single most important non-trivial design issue for templates and output generation in general, is how to best facilitate the referencing of "asset" files:

    * We want a uniform concise way of referring to them, which does not require absolute paths to be specified, and makes it easy to move files around.
    * We want addons to be able to contain their own localized isolated asset files (even when such files appear to be elsewhere to the visitor).
    * We want the coder (and other pack authors) to be able to selectively replace arbitrary asset files, much like a skin might override default files, non-invasively.
    * We'd like to avoid forcing the user into listing/defining every single asset file.



A Strategy for Referencing Asset Files
----------------------------------------

We adopt the following strategy when it comes to asset files:

    * We use a "global" alias system that holds short, dynamically created aliases to file paths.
    * Some items will have both file paths and url paths; in such cases we want a uniform pattern for naming both.
    * Addons and sites can register aliases that can be referred to in templates and in code, e.g. "${aliaspath}/views/viewfile.jn2"
    * To enable users and addons to replace asset files non-invasively, developers can specify non-invasive replacements for asset files.  This can be done in several ways, but the easiest is to specify a mirror-like directory, which is scanned on startup and instructs mewlo to replace any file found with same path.


What can you do with Asset Manager
-----------------------------------

Borrowing from pyramid, the asset system can be used to:

    * Refer to a file (or directory) as being relative to a pack/alias (rather than by absolute path)
    * Refer to a file/directory as relative to some current context
    * Tell mewlo to make files/directory available as if they were in public html accessible area.
    * In the above case we have multiple options, including asking mewlo to physically copy them (and recopy when they change), or to serve them per request, performing some kind of authentification check.
    * Generate urls for both internal and external links
    * Be smart about whether to use https or http when generating links.
    * Allow users/addons to override/intercept pre-existing assets with replacements



Caching from modular directories to public area
-----------------------------------------------

Yii has a clever feature that automatically caches and copies static resources from local (plugin) directories into the publicly servable directories (where standard web browser can serve them).

Mewlo will support such a function.

Mewlo has a way to specify a controller that serves static files in a given directory, as if they were exposed under some virtual url route.

This function can be used IFF we want the python web server to serve up the files, possibly with access permission checks, access counting, etc.  The drawback to serving such files in this fashion is the consumption of cpu resources and web server instances.  Most python frameworks advise against using python web server for serving static files (which i find troubling and ill-boding).

So Mewlo will offer an alternative option that will dynamically copy static resources from local sources to a dynamic public exposed area where they can be accessed directly via a standard web server.

Such a configuration would look something like this:

MewloSite.ExposeStaticFiles(PrivateSourceDirectory, PublicUrl, PublicUrlFileDirectory)

This tells mewlo that the (recursive) files under PrivateSourceDirectory should be served under the url PublicUrl.
And that this should be done EITHER by acting as a virtual proxy and actively serving files itself,
or by ensuring a mirror copy of the files is copied to the PublicUrlFileDirectory where another web server (apache) can serve them.

Some issues worth nothing:

A common use for this functionality will be to let addons expose css or static (image) files.
So there needs to be an easy way for an addon to specify that such exposing should be done and handled however the developer chooses to handle such cases.
We can do this by using aliases, e.g.:

    * MewloSite.expose_static_files("${myaddon_filepath}/static_files/", "${mewlo_static_url}/myaddon/", "${mewlo_static_filepath)/myaddon/")


A simpler way
-------------

Alternatively, we could be more restrictive in the allowed paths, and say that it should look like:

    * MewloSite.expose_static_files(PrivateSourceDirectory, unique_subdirectory_identifier)

Where the PublicUrl and PublicUrlFileDirectory would be constructed automatically from some base paths.

One thing to note is that, the ExposeStaticFiles call gives mewlo enough information to handle any url route to ${mewlo_static_url} and serve the files.  If this url route is exposed publicly to a traditional web server, then that web server will serve up the files, and the routes will never be seen by mewlo.

In this way, we don't have to worry about telling Mewlo when a path/url is one it will HAVE to handle requests for or whether the path will be intercepted by a traditional web server.

However, if we knew that we wanted mewlo to serve the files internally, there would be no point in COPYING the files to the PublicUrlFileDirectory, as such an action is unnescesary if the files are being served internally by Mewlo.

Furthermore, we might want to consider is whether we need to deal with a case where we will want SOME files to be served internally from one directory, while other files we want to copy and have a traditional web server handle.

What would be the best way to handle such a thing?

Perhaps the simplest way would be to let the config specify a url path+directory that a traditional webserver will handle (optional), and a url path for internal serving of files, and then let config specify the DEFAULT way of handling static files (copy+traditional vs internal).  But also let config specify that certain unique_subdirectory_identifier values should be handled in specific way (internal vs copy+traditional).

A call like:

    * MewloSite.expose_static_files(PrivateSourceDirectory, unique_subdirectory_identifier)
    
Does not say whether the files in PrivateSourceDirectory/ are to be served internally, or copied somewhere to be served by a traditional web browser.
Such calls are agnostic on this front, and may be made by plugins, addons, etc.

Then, depending on site options, we will dynamically create aliases for the urls and filepaths of the files covered by that unique_subdirectory_identifier, as ${asset_url_unique_subdirectory_identifier} and ${asset_dir_unique_subdirectory_identifier}.

So the other piece of info that needs to be specified in a site config is a map from each unique_subdirectory_identifier to either:
    * An internal url, for internal file serving (and we need to set up a route to catch such requests)
    * An external url, and an external file directory where we will pre-copy files for serving by an external/traditional web browser.

Let us call the former things, AssetSources and the latter things, AssetMountpoints.

So, every AssetSource must be mounted on one and only one AssetMountpoint.
In the simplest case we will have a single AssetMountpoint, acting as a default AssetMountpoint.  So all AssetSources will be served internally or copied and served via traditional web browser.
In a more complicated case we may have multiple AssetMountpoints, and attach different AssetSources to different AssetMountpoints.


Static file Route and NavNode
-----------------------------

Left unaddressed in this description of serving static files is any reference to Routes and NavNodes.
In early Mewlo work, we served static files by adding a controller and route to a custom site as follows:

        routegroup.append(
            MewloRoute_StaticFiles(
                id  = 'static_files',
                path = '/static',
                controller = MewloController_StaticFiles(
                    sourcepath = '${sitefilepath}/public_html'
                    ),
                ))

This works fine -- it internally serves files under a certain source path as if they were at a certain url path.  It handles such requests like any other route-controller request, and provides all the benefits that come along with using a normal route system.

When we want to refer to a static resource in '${sitefilepath}/public_html/FILENAME' we instead link to '/static/FILENAME'.


How other frameworks do it
--------------------------

    * http://www.yiiframework.com/wiki/148/understanding-assets/
    * https://gist.github.com/jasonhancock/5073938
    * https://docs.djangoproject.com/en/dev/howto/static-files/
    * https://docs.djangoproject.com/en/dev/howto/static-files/deployment/