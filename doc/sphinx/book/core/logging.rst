Logging
=======


Mewlo must have an extremely robust logging system, because aiding administration of busy sites is a key goal of Mewlo.

Some features of the logging system:

    * Flexible log browsing and searching, including links to "objects" referred to in log entries.
    * Flexible filtering of log events into different log tables and automatic creation of log files/tables.
    * Flexible ways of emailing/alerting on certain log events.
    * Flexible automatic archiving of log events between tables based on age and filters, or deleting of old log events.

One interesting issue with Logging is that for serious sites we usually want to log to a database, BUT there are times when that can be problematic, such as when database connectivity fails, or at early startup.  It would be nice to have a unified system that could smartly fall back on file-based logging for certain early events or when database connection fails.

Closely related to logging is the issue of monitoring and displaying debug information while testing code.  What support do we provide for such things?


Unresolved logging issues

    * Cases where sometimes we want to have a log target capture a log message and NOT allow further log targets to get it; but sometimes we want multiple targets to log it.
    * We have cases where an object is part of a log message (Request object), and how it should be handled when writing to log file or database


Todo:

    * Add Apache logging format as an option
