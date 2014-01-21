Updating 2
==========

One possible update scheme:

Web/code updates could work like this:

    * We have three special directories, one for Updates_Pending, one for Updates_Installed, and one for Updates_Backups.
    * Admins can manually download and put zip files into Updates_Pending directory, OR our tool can auto fetch from web zip files into that directory.
    * Admin pages can REPORT on pending updates available in the Updates_Pending directory (inspecting zips for info).
    * Updates should describe what's new and the nature of any database updates that will need to be run.
    * At start of app, it can bootstrap unpack and install those zip files at the start, if commandline says to, or simply report Updates_Pending are available.
    * So normal behavior will be to check for updates and if found, report, and EXIT; a commandline option says to install updates; another says to run and ignore.
    * After installation, zip files are appended with datetime and MOVED to the Updates_Installed directory.
    * To be really nice, we might zip up ENTIRE system directory and store as a timestamped file backup when running updates.


Database updates could work like this:

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


