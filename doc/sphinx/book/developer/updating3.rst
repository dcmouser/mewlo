Updating 3
==========

How do other CMS systems handle updating (core vs module)?



Wordpress
---------

    * http://wp.tutsplus.com/tutorials/plugins/a-guide-to-the-wordpress-http-api-automatic-plugin-updates/
    * http://halfelf.org/2011/how-the-wordpress-upgrade-works/?ModPagespeed=noscript

From wordpress - http://halfelf.org/2011/how-the-wordpress-upgrade-works/?ModPagespeed=noscript:

    * "Most of the time, we all see the plugin and theme installer, where it downloads the plugin to /wp-content/upgrade/, extracts the plugin, deletes the old one, and copies up the new one. Since this is used more often than the core updater (most of the time), it's the sort of upgrade we're all used to and familiar with. And we think 'WordPress deletes before upgrading, sure.' This makes sense. After all, you want to make sure to clean out the old files, especially the ones that aren't used anymore.This is not how a core update works."

    * "WordPress core updates, the ones to take you from 3.0.3 to 3.0.4, do not run a blanket delete. They don’t even run a variable delete. They don't even run a wild-card delete on files in wp-admin (which they could). Instead they have a manually created list of files to delete, files that have been deprecated, and delete only those files."

    * "Once the old files are listed, remember that we have not deleted anything, the upgrader runs through 9 steps:

    * Download the zip file of the new release, unzip it and delete the zip
    * Make sure the file unzipped!
    * Make a .maintenance file in WordPress base (this makes your blog 'down for maintenance' so no one can do anything and screw you up mid-stream
    * Copy over the new files. This is a straight copy/replace. Not delete.
    * Upgrade the database. This may or may not happen.
    * Delete the unzipped file
    * Delete the .maintenance file
    * Remove the OLD files. This is where it goes through the list of deprecated and unused files and deletes them.
    * Turn off the flag that tells you to upgrade every time you're in wp-admin"



Drupal
------

    * https://drupal.org/node/250790
    * http://drupaleasy.com/blogs/ultimike/2010/08/fast-safe-module-updates-drush-svn
