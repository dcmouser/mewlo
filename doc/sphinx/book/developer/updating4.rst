Updating 4
==========

Can we break up the update procedures into smaller more manageable tasks? Listed in no particular order:

    * Check online if a new updated version of a pack is available
    * Report on new versions available
    * Download a new version as a zip file and place it somewhere for later installation
    * Delete an existing installed pack
    * Unpack a downloaded zip pack to install it
    * Having a pack check if it needs to run a database update or if database is incompatible
    * Have a pack make a database update


To attack the problem, lets start by avoiding the issues with DOWNLOADING and INSTALLING new updated packs, and do the other stuff first, assuming that admin will do the file installs manually for now.


What do the update check functions *return*?  How do we report back information about update checks, and in what form?
We want this information to be reportable on a web page (with links to perform specific updates), or on commandline, etc.


One strategy:

    * Each pack will have a text/html field that will describe their update "status" -- the result of the last update check/run.  Or two fields (one for update check one for update run).
    * This field will describe the date of last check, the results, any errors from update checking or installation.
    * This approach would be well suited for presenting a web page listing the status for each pack.


An alternative related strategy:

    * For each pack keep a dedicated log file for each pack, and log any update related checking/errors/etc to such a file.
    * We could display the recent items from this log on a page listing the status of each pack.
    * A good aspect of this is we would keep long-term logs of update-related errors, etc.
    * A downside is having to use a completely independent different kind of logging system for such messages.
    * We could alternatively try to tie into the normal logging system but that could be problematic because the normal logging system may not be up and running when update checking occurs, and because it would be hard to extract per-pack info for display.


A hybrid strategy:

    * Use standard log system to log update related messages, for posterity.
    * Use a dedicated transient text field for each pack listing the results of last update check info.
    * I like this approach.


Do we need to differentiate between database updates and file updates, and how? What about:

    * Each pack has text field for "Package (web) version status:"
    * Each pack has text field for "Database version status:"
    * Each pack has text field for "Requirements status:"


