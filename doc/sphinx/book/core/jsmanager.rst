Javascript Manager
==================


Mewlo includes a lightweight javascript manager/helper that should be used to load javascript code on a page.  It may also be used to add css files.

If one was handcoding a web page, and wanted to use a library like jquery, you would put at the top of the web page something like:

    <script src="/mysites/myjslibraries/jquery/jquery-2.1.0.js" type="text/javascript"></script>

There are several problems with such an approach:

    * We want code to be DRY -- we don't want to specify filepaths and names on multiple web pages.
    * We want a centralized place to be able to update jquery and other js library versions.
    * We want to make it easy to change the location where js libraries are served from, and change the versions served easily (minified or uncompressed for testing, etc.)
    * We don't want to have to worry about generating the page head html at the right time during page generation
    * We don't want to worry about multiple includions of the same library files if different addons and independent page building functions need it.

The javascript manager helps us to solve these problems.

First, at any time during response generation, the coder may invoke something like this:

    * sitecomp_jsmanager().include_jslibrary('jquery', request)
    
This instructs the javascript manager to include the necesary head html script(s) for the rendered page, whenever that rendering occurs, and ignores duplicate requests.

The javascript manager uses the asset system and knows how to mount the assets for such libraries so as to expose them.  This makes it easy for the manager to copy js files to a public webserver directory, or serve files internally from mewlo, or use alternate versions, or link to external content delivery network if desired.  The user does not need to worry about placing js library files in the correct public places, the asset system handles this automatically.

The javascript manager also registers some aliases to make it safe and easy to refer to subdirectories and js components safely from within template files.

