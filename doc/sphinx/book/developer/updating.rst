Updating 1
==========

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

    * Do we want/need to use a separate script/tool/process to do updating?
    * We need a simple way to have the site "shut down" during maintenance (but allow admin access?); what does this kind of maintenance mode look like?
    * Unlike something like wordpress, Mewlo is for coders so we dont have to be as hand-holdy and we won't have as many installs.
    * Overwriting existing files: Because python web apps stay resident, any update procedure has to either run at startup before any web access is allowed, OR block all normal web access except admin update pages. There is a way for python modules to be re-loaded without restarting but it seems frought with danger.
    * Note that "checking" if updates are available has to be separate from actually "performing" update procedures, which always are going to require admin approval, because of he possibility of problems.







