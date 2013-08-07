"""
This module defines classes and functions that assist in logging.

There are multiple classes that work together to create our logging system:
* LogManager - the main supervisor class that manages a collection of Loggers
* Logger - responsible for saving/writing a log event to some destination, and matching log events to decide whether to handle them
* LogMessage- a single loggable event/message
* LogFilter - class responsible for deciding if a log message should be handled by a Logger; each logger has a list of zero or more LogFilters to check for match
* LogTarget - destination targets for loggers; each logger has a list of LogTargets to send to on match

How these classes co-exist:
* A site has a single LogManager; all logging functionality is done through that manager.
* A LogManager manages a collection of zero or more Loggers
* A Logger has a collection of zero or more LogFilters and a collection of one or more LogTargets
* A triggered LogMessage is sent to the LogManager which sends it to each Logger; if a message passes the filters for a Logger, it triggers the targets for that logger

What are the goals of the logging system?
* Provide a convenient syntax for adding both simple and complex logging messages
* Support log messages with useful information like:
** a dotted id path, to aid in filtering messages (e.g. "authentification.openid.yahoo")
** numerical severity level, to aid in filtering messages and deciding who to email them to (e.g. from -100 to +100)
** a short message "type", again to aid in filtering (e.g. "error" | "warning")
** extras dictionary of arbitrary data to be serialized/stringified
* Allow a collection of loggers to be configured that process log messages in different ways.  Each Logger may:
** Filter on which log messages it cares about based on various patterns
** Decide how to handle the log message, with targets that include:
*** Emailing log messages
*** Saving log messages to text files (rotating or otherwise(
*** Storing log messages in database tables
* Additionally we would like to support things like queuing log messages for deferred handling (useful if we want to log to database but database is not set up yet).
* Smart throttling if we are being overwhelmed with log messages
* Smart digesting, if we have a bunch of messages to email we might want to send onlyh one email with all log messages for a given session

Some examples of things we will want to be able to easily do:
* on severe errors trigger an email to admin
* log "debug" messages to file only
* discard warning messages when running in production mode
* log messages of type x|y|z to database tables x,y,z

"""


# Mewlo helpers
from mewlo.mpackages.core.helpers.debugging import smart_dotted_idpath


class LogManager(object):
    """
    LogManager - the main supervisor class that manages a collection of Loggers
    """

    def __init__(self, site):
        self.loggers = []
        self.set_parent(site)

    def set_parent(self, parent):
        self.parent = parent
    def get_parent(self):
        return self.parent


    def add_logger(self, logger):
        """Just add a child logger to our collection."""
        self.loggers.append(logger)
        # let logger know it's parent
        logger.set_parent(self)

    def process(self, logmessage):
        """Process a LogMessage, by allowing each of our attached loggers to handle it."""
        for logger in self.loggers:
            logger.process(logmessage)




class LogFilter(object):
    """
    LogFilter - class responsible for deciding if a log message should be handled by a Logger; each logger has a list of zero or more LogFilters to check for match
    """

    def __init__(self):
        self.andfilters = []
        self.parent = None

    def set_parent(self, parent):
        self.parent = parent
    def get_parent(self):
        return self.parent

    def add_andfilter(self, filter):
        # add a chained filter which is treated like an AND
        self.andfilters.append(filter)
        # let filter know it's parent
        filter.set_parent(self)

    def doesmatch_full(self, logmessage):
        """Check if the logmessage matches our filter (or ALL of them if there are multiple chained with us."""
        # first check against ourself, if fail, then no point going any further
        if (not self.doesmatch_us(logmessage)):
            # doesn't match our condition
            return False
        # it matched us, now let's make sure it matches ALL of our AND filters (if any)
        if (not self.doesmatch_andchains(logmessage)):
            # doesn't match one of our registered AND chain of filters
            return False
        # it's good!
        return True


    def doesmatch_andchains(self, logmessage):
        """Check if logmessages matches any attached "AND" chained filters (we may have none)."""
        # test ALL and reject if any reject
        for filter in self.andfilters:
            if (not filter.doesmatch_full(logmessage)):
                return False
        # it matched ALL, so it's good
        return True



    def doesmatch(self, logmessage):
        """This is the exposed public function to check if a logmessage matches the filter. It will normally be implemented by a subclass."""
        # parent class just returns True so it will always match
        return True





class LogTarget(object):
    """
    LogTarget - targets for loggers; each logger has a list of LogTargets to perform on match
    """

    def __init__(self):
        self.parent = None

    def set_parent(self, parent):
        self.parent = parent
    def get_parent(self):
        return self.parent

    def process(self, logmessage):
        """Process the target action (write to file, save to database, emailing, etc.).  This should be overridden by subclass to do actual work."""
        print "Activating base LogTarget action, which is to write log message to screen: "+logmessage.debug()+"\n"
        pass









class Logger(object):
    """
    Logger - responsible for saving/writing a log event to some destination, and matching log events to decide whether to handle them.
    """

    # class constants
    # a logmessage can have a severity level (negative or postitive)
    DEF_LEVEL_default = 0
    # default message dotted "id" which is just used for easy filtering and searching
    DEF_MESSAGEID_default = None
    # shorthand logmessage "types"
    DEF_MTYPE_error = 'ERROR'
    DEF_MTYPE_warning = 'WARNING'
    # we can throttle when log messages are generating too rapidly
    DEF_THROTTLERATE_default_messages_per_sec = 60


    def __init__(self, id, throttlerate = DEF_THROTTLERATE_default_messages_per_sec):
        self.id = id
        #
        self.filters = []
        self.targets = []
        self.deferredmessages = []
        #
        self.throttlerate = throttlerate
        #
        self.parent = None

    def set_parent(self, parent):
        self.parent = parent
    def get_parent(self):
        return self.parent
    def get_id(self):
        return self.id


    def add_filter(self, filter):
        """Append a filter.  Multiple appended filters are treated like OR conditions (you can simulate AND by chaining filters together."""
        self.filters.append(filter)
        # let filter know it's parent logger
        filter.set_parent(self)

    def add_target(self, target):
        """Append a target.  Targets will be run when the filters match. Multiple appended targets will be run in sequence."""
        self.targets.append(target)
        # let target know it's parent logger
        target.set_parent(self)



    def process(self, logmessage):
        """Process a LogMessage.  This may involve ignoring it if it doesn't match our filters, or sending it to Targets immediately if it does."""
        if (self.doesmatch_filters(logmessage)):
            self.run_targets(logmessage)


    def doesmatch_filters(self, logmessage):
        """Return True if this message matches ANY of the filter(s) for the logger.."""
        # if no filters added, then it's an automatic match
        if (len(self.filters)==0):
            return True
        # see if any filter matches it
        for filter in self.filters:
            if (filter.doesmatch_full(logmessage)):
                return True
        # nothing matched, so it's false
        return False


    def run_targets(self, logmessage):
        """Run ALL registered targets on the message."""
        for target in self.targets:
            target.process(logmessage)






class LogMessage(object):
    """
    LogMessage- a single loggable event/message
    """

    def __init__(self, msg, mtype, level=Logger.DEF_LEVEL_default, id=Logger.DEF_MESSAGEID_default, extras={}):
        # constructor for log message
        self.msg = msg
        self.mtype = mtype
        self.level = level
        self.id = id
        # extra dictionary (note we COPY (shallow) the dictionary because we dont want to get a dictionary that may be modified by caller or which we may add to and affect caller
        self.extra = dict(extras)

    def as_logline(self):
        """Get the LogMessage as a (default formatted) string suitable for writing to a log file.  Subclasses would be expected to override this function."""
        return str(self.msg)

    def debug(self, indentstr=""):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        return indentstr+"LogMessage: "+self.as_logline()



