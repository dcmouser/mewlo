Issues to Resolve
=================

Hard Issues:
------------

    * SQL Alchemy (which I propose to use for ORM) has several ways of handling inheritance in databases; need to decide which of these is most appropriate for our desire to refer to different kinds of objects -- for example to let the ACL use users/groups/etc as subject and object of rules: http://docs.sqlalchemy.org/en/rel_0_7/orm/inheritance.html
    * How to resolve inheritance and pointers to different kinds of objects in things like ACL tables and log tables?
    * How to best support cloud/cluster/replication/multi-server setups?
    * How to best implement a full-text search system across multiple content types, etc?
    * What's the best way to do support pervasive addon support while keeping these plugins non-invasive, isolated, and easy to update?
    * To what extent can we (and do we want to) structure as much core code as possible in the form of a standard Mewlo "extension" with support for update checking, etc.
    * What's the best way to organize configuration files?
    * What's the best way to support multiple "sites" run from the same mewlo base install?
    * What's the best way to support update checking and installation, given that administration will normally be done from web admin? To what extent should it interoperate or depend on standard "package managers?
    * To what extent should we break up the code into official online-installable python "packages"
    * What fields should we put in the User model table vs which fields should be in secondary tables; what's the best way to store arbitrary profile fields.
    * What's the best approach to handling/formatting/returning errors/warnings, and to what extent should exceptions be used.
    * Whether to build on top of no framework, a tiny framework, or a large framework?

        * Start on large framework (pyramid)
        * Dont call any framework funcs if possible
        * Move to small framework
        * Eventually replace framework



Easier Issues:
--------------

    * What's the best way to allow addons and the core to automatically update the database structure? 
    * Use drupal-like approach; plugin API allows plugins to store installed database version to compare to code database version and run database update as needed.
    * What's the best way to organize and store site settings in a database an make them available for admin modification vs. settings distributed in multiple configuration files in addon directories.
    * What's the best way to handle "unread" posts type tracking?
    * See http://stackoverflow.com/questions/2288814/php-forums-how-to-cope-with-unread-discussions-topics-posts/5045827#5045827
    * How to build support for gracefully handling overloaded server?
    * We will provide a "Server Load" API that functions can interact with, much like the throttling API, in order to gracefully fail.  This API should support some backend configuration and notification config.
    * What's the best way to handle anonymous visitors in terms of tracking info alongside with registered user tracking?

        * First, i propose we reserve a number of early "reserved" special user accounts that have reserved meanings: Admin, AnonymousWebUser, CronUser, FeedUser, WebSpiderUser, etc.
        * Secondly, for EVERY case/table where we record a userid, we ALSO need to log the user IP; this is also useful for cases where one user account is used (abused?) from multiple IPs.

    * What's the best way to support replaceable components?

        * This is a different issue from allowing the ADDITION of packs and plugins.
        * It deals with the ability to drop-in replacement components for core classes.
        * I believe the key way this needs to be solved is to avoid hardcoding imports and object instantiation classes.
        * Instead all importing of modules and object instantiation should route through the Mewlo system, which can be configured to use drop-in replacement classes for any component (including User component, etc.)
        * So instead of "import mewlo.core.User; myuser = User.user()" we would instead have "import mewlo.core.ComponentManager; ComponentManager.DoImport("User"); mysuser = ComponentManger.CreateObject("User.user");




