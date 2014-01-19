Updating
========

This document discusses the mewlo api involved in updating stuff -- mostly database, when new versions of a mewlo app or mewlo itself is released.

Let's think about different kinds of things a package might do related to update operations:

    * Detect if the current package code needs to run a database update before it can run (ie after a code update but before database update).
    * Detect if the pre-requisites are not met for a package.
    * Detect if there is an incompatibility problem with the current code and the database.
    * Detect if there is a pending online update that is optional or security-essential.
    * Detect if there is a locally available code update that has been downloaded and is waiting to unpack.
    * Allow user to block a package from online update checking
    * Installing new packages from online repository

Ok let's separate the easy form the hard:

    * Easy and low-risk: Checking for updates online, refusing to run if database updates needed.
    * Medium and medium-risk: Actually running database updates, halting execution until db updates applied
    * Hard and high-risk: Applying file updates over existing files





Some issues:

    * Do we want/need to use a separate process to do updating?
    * We need a simple way to have the site "shut down" during maintenance (but allow admin access?); what does this kind of maintenance mode look like?
    * Unlike something like wordpress, Mewlo is for coders so we dont have to be as hand-holdy and we won't have as many installs.







Overwriting existing files:

Because python web apps stay resident, any update procedure has to either run at startup before any web access is allowed, OR block all normal web access except admin update pages.
(There is a way for python modules to be re-loaded without restarting but it seems frought with danger).


Checking if updates are available has to be separate from running update procedures, which always are going to require admin approval, because of he possibility of problems.













One possible scheme:

Web/code updates will work like this:

    * We have three special directories, one for Updates_Pending, one for Updates_Installed, and one for Updates_Backups.
    * Admins can manually download and put zip files into Updates_Pending directory, OR our tool can auto fetch from web zip files into that directory.
    * Admin pages can REPORT on pending updates available in the Updates_Pending directory (inspecting zips for info).
    * Updates should describe what's new and the nature of any database updates that will need to be run.
    * At start of app, it can bootstrap unpack and install those zip files at the start, if commandline says to, or simply report Updates_Pending are available.
    * So normal behavior will be to check for updates and if found, report, and EXIT; a commandline option says to install updates; another says to run and ignore.
    * After installation, zip files are appended with datetime and MOVED to the Updates_Installed directory.
    * To be really nice, we might zip up ENTIRE system directory and store as a timestamped file backup when running updates.


Database updates work like this:

    * On startup of server, every package (including core package) is responsible for checking if any databases updates are needed.
    * Normally this will simply be a matter of querying each MODEL whether any database update is needed.
    * If any database update is needed, it is reported and server will refuse to run (or only serve limited admin pages).
    * Server commandline option needs to be passed to actually run database updates.
    * Before running updates, ideally we can export backup of tables (or entire database) with timestamps to Updates_Backups folder; server commandline to bypass.  Note that when we save a backup of the database table we need to also export the package settings data for it.
    * The code knows what the code/latest version of the database table is.
    * When upgrading/installing a database update, the package can store the database "version#" in the persistent package settings database table.
    * So when checking whether update is needed (and which version to go from-to, we read this table database version# and compare it to code database version#.
    * The upgrade procedure should know how to go from any table-installed version to any code version (except of course that it can fatal error if asked to downgrade).
    * On initial install it will simply be a matter of running simple sqlalchemy make database table.
    * Alternatively if we are concerned about persistent package stored database version# not matching actual table version on cases where user might have restored it, we might consider a special table where we map tablename,tableversion -> table scheme text.
    * Using that table, would have 2 purposes.  It will allow us, at startup to verify the actual version# of each existing database table.
    * That will enable us to not just correct mismatched database version#, but detect at startup any conflict with the actual and expected database scheme for a table.
    * It is up to model or package to perform sql-based table alterations.


















How do other CMS systems handle this stuff?







Wordpress:
    * http://wp.tutsplus.com/tutorials/plugins/a-guide-to-the-wordpress-http-api-automatic-plugin-updates/
    * http://halfelf.org/2011/how-the-wordpress-upgrade-works/?ModPagespeed=noscript

From wordpress - http://halfelf.org/2011/how-the-wordpress-upgrade-works/?ModPagespeed=noscript:

"Most of the time, we all see the plugin and theme installer, where it downloads the plugin to /wp-content/upgrade/, extracts the plugin, deletes the old one, and copies up the new one. Since this is used more often than the core updater (most of the time), it's the sort of upgrade we're all used to and familiar with. And we think 'WordPress deletes before upgrading, sure.' This makes sense. After all, you want to make sure to clean out the old files, especially the ones that aren't used anymore.This is not how a core update works."

"WordPress core updates, the ones to take you from 3.0.3 to 3.0.4, do not run a blanket delete. They don’t even run a variable delete. They don't even run a wild-card delete on files in wp-admin (which they could). Instead they have a manually created list of files to delete, files that have been deprecated, and delete only those files."

"Once the old files are listed, remember that we have not deleted anything, the upgrader runs through 9 steps.

    Download the zip file of the new release, unzip it and delete the zip
    Make sure the file unzipped!
    Make a .maintenance file in WordPress base (this makes your blog 'down for maintenance' so no one can do anything and screw you up mid-stream
    Copy over the new files. This is a straight copy/replace. Not delete.
    Upgrade the database. This may or may not happen.
    Delete the unzipped file
    Delete the .maintenance file
    Remove the OLD files. This is where it goes through the list of deprecated and unused files and deletes them.
    Turn off the flag that tells you to upgrade every time you’re in wp-admin"




Drupal:

https://drupal.org/node/250790
http://drupaleasy.com/blogs/ultimike/2010/08/fast-safe-module-updates-drush-svn
