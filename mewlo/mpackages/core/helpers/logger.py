"""
This module defines classes and functions that assist in logging.

There are multiple classes that work together to create our logging system:
* LogManager - the main supervisor class that manages a collection of Loggers
* Logger - responsible for saving/writing a log event to some destination, and matching log events to decide whether to handle them
* LogMessage- a single loggable event/message
* LogFilter - class responsible for deciding if a log message should be handled by a Logger; each logger has a list of LogFilters to check for match
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



class LogManager(object):
    """
    LogManager - the main supervisor class that manages a collection of Loggers
    """

    def __init__(self):
        self.loggers = []


    def process(self, logmessage):
        """
        Process a LogMessage, by allowing each of our attached loggers to handle it.
        """
        for logger in self.loggers:
            logger.process(logmessage)


    def add_logger(self, logger):
        self.loggers.append(logger)





class LogFilter(object):
    """
    LogFilter - class responsible for deciding if a log message should be handled by a Logger; each logger has a list of LogFilters to check for match
    """

    def __init__(self):
        self.andfilters = []

    def add_andfilter(self, filter):
        # add a chained filter which is treated like an AND
        self.andfilters.append(filter)

    def doesmatch_full(self, logmessage):
        # we check if it matches our filter, and any "chained" filters which are treated as ANDS
        if (not self.doesmatch_us(logmessage)):
            # doesn't match our condition
            return False
        if (not self.doesmatch_andchains(logmessage)):
            # doesn't match any of our registered AND chain of filters
            return False
        # it's good!
        return True


    def doesmatch_andchains(self, logmessage):
        # does the message match ALL of our attached "AND" chained filters (we may have none)
        if (len(self.andfilters)==0):
            # no registered and filters, so its considered matched
            return True
        # test ALL and reject if any reject
        for filter in self.andfilters:
            if (not filter.doesmatch_full(logmessage)):
                return False
        # it matched ALL, so it's good
        return True



    def doesmatch(self, logmessage):
        # does the message match OUR filter
        # this function would normally be implemented by a subclass
        # parent class just returns True so it will always match
        return True





class LogTarget(object):
    """
    LogTarget - targets for loggers; each logger has a list of LogTargets to perform on match
    """

    def __init__(self):
        pass

    def run(self, logmessage):
        # run the target on the logmessage -- this typically means writing it to file, saving it in database, or emailing it.
        print "\n\n\n************* IN LOGTARGET ***********************\n"
        print logmessage.debug()
        print "\n"
        pass









class Logger(object):
    """
    Logger - responsible for saving/writing a log event to some destination, and matching log events to decide whether to handle them
    """

    # class constants
    DEF_LEVEL_default = 0
    #
    DEF_MESSAGEID_default = None
    #
    DEF_MTYPE_error = 'ERROR'
    DEF_MTYPE_warning = 'WARNING'
    #
    DEF_THROTTLERATE_default_messages_per_sec = 60


    def __init__(self, id):
        self.id = id
        #
        self.filters = []
        self.targets = []
        self.deferredmessages = []
        #
        self.throttlerate = self.DEF_THROTTLERATE_default_messages_per_sec


    def add_filter(self, filter):
        self.filters.append(filter)

    def add_target(self, target):
        self.targets.append(target)



    def process(self, logmessage):
        """Process a LogMessage.  This may involve ignoring it, queing it, or writing it out immediately."""
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
            target.run(logmessage)






class LogMessage(object):
    """
    LogMessage- a single loggable event/message
    """

    def __init__(self, msg, mtype, level, id, extras):
        # create a new log message
        self.msg = msg
        self.mtype = mtype
        self.level = level
        self.id = id
        # extra dictionary
        self.extra = dict(extras)


    def debug(self, indentstr=""):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        return indentstr+"LogMessage: "+str(self.msg)



