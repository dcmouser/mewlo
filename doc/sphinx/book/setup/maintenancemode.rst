Maintenance Mode
================

There are different ways that a mewlo site can be in an offline/maintenance mode.  This document describes them.

Let's consider some options:

    * A site may be forced offline because of a configuration problem or a module that needs an update, etc.  In this case the internal site check knows the reason it is being forced offline.
    * A site may temporarily be forced offline while performing an update procedure.
    * A site may be manually taken offline by the administrator, for an administer-defined reason.  Administrators may be allowed to access the site but end users shown a custom message.
    * For sites manually taken offline -- how should administrator set this flag, how should they set the offline message?
    * There may be other semi-offline states (like a read-only state, or a no-new member state).
