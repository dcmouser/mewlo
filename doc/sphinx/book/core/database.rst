Database ORM API
================


We propose to use the SQLAlchemy library to handle all database/orm functionality.
This breaks with our general approach of not using existing 3rd party libraries, but it's one of the few areas where we really don't want to reinvent the wheel.

It would be nice if we could isolate and wrap the SQL Alchemy functionality in our own layer to make it easier to port and swap out SQLAlchemy but i'm not sure that's really feasible.

We can however, list some desires we have for the ORM codebase:

    * A major concern is keeping code and configuration DRY: We don't want to have to repeat field definitions, labels, validation, GUI widget hints, etc.
    * We will want to support database table upgrading when modules are upgraded.
    * We want to support distributed databases, and ability to put different tables on different databases, etc.
    * Good logging and tracking of database operations for performance analysis and debugging.
    * Handle hierarchical class structures well (see Programming Issues to Resolve).