In the configuration of the site, we typically instruct mewlo that this directoriy is a potential shadow for mewlo assets.
Each subdirectory here matches an mpack id.

On startup, mewlo will scan this directory (and all subdirectories) looking for view and other static files that will override those under the main mewlo directory.

This is an easy way to non-invasivly replace any built-in view (or static) file in any mewlo package (core or plugin/addon).

IMPORTANT: Note that it won't work for python CODE files, just static files and assets like views, js, css, html, images, etc. That are loaded dynamically.

NOTE: Mewlo has an ability to copy files from mpack directories into an external static asset serving directory (where another web server will see and serve the files); this is done AFTER the replacement-shadowing specified in this directory, and so the files exposed and copied will be the replaced files (as one would want).


