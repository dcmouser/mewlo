Reinventing the Wheel vs. Using Existing Code
==============================================


Mewlo tries to strike a balance between reinventing the wheel and using existing best-in-class, third-party, open source code.

The following is a list of the 3rd code libraries that Mewlo makes use of:

    * SqlAlchemy - For the high-level database ORM functionality.  This is a large, proven codebase that handles all access to the database system.
    * Jinja2 - The template output system.  We may decide to switch template engines at some point (mako?) but we will not be making our own and we will choose ONE and mandate it.

And these small python helper modules:
    * Requests - web downloading - http://docs.python-requests.org/en/latest/index.html


In addition, we are currently using the following as a stop-gap measure, but are likely to replace:

    * Werkzeug - Low level http request/response processing.


Other areas of likely 3rd party code use:

    * Javascript/Ajax libraries.
    * Internationalization library.
    * Form library (maybe WTForms?)
