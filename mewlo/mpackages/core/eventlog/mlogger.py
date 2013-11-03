"""
mlogger.py

This module defines classes and functions that assist in logging.

There are multiple classes that work together to create our logging system:
    * LogManager - the main supervisor class that manages a collection of Loggers
    * Logger - responsible for saving/writing a log event to some destination, and matching log events to decide whether to handle them
    * LogFilter - class responsible for deciding if a log message should be handled by a Logger; each logger has a list of zero or more LogFilters to check for match
    * LogTarget - destination targets for loggers; each logger has a list of LogTargets to send to on match

How these classes co-exist:
    * A site has a single LogManager; all logging functionality is done through that manager.
    * A LogManager manages a collection of zero or more Loggers
    * A Logger has a collection of zero or more LogFilters and a collection of one or more LogTargets
    * A triggered logmessage(Event class) is sent to the LogManager which sends it to each Logger; if a message passes the filters for a Logger, it triggers the targets for that logger

What are the goals of the logging system?

    * Provide a convenient syntax for adding both simple and complex logging messages
    * Support log messages with useful information like:
        * a dotted id path, to aid in filtering messages (e.g. "authentification.openid.yahoo")
        * numerical severity level, to aid in filtering messages and deciding who to email them to (e.g. from -100 to +100)
        * a short message "type", again to aid in filtering (e.g. "error" | "warning")
        * extras dictionary of arbitrary data to be serialized/stringified
    * Allow a collection of loggers to be configured that process log messages in different ways.  Each Logger may:
        * Filter on which log messages it cares about based on various patterns
        * Decide how to handle the log message, with targets that include:
            * Emailing log messages
            * Saving log messages to text files (rotating or otherwise(
            * Storing log messages in database tables
    * Additionally we would like to support things like queuing log messages for deferred handling (useful if we want to log to database but database is not set up yet).
    * Smart throttling if we are being overwhelmed with log messages
    * Smart digesting, if we have a bunch of messages to email we might want to send onlyh one email with all log messages for a given session

Some examples of things we will want to be able to easily do:
    * on severe errors trigger an email to admin
    * log "debug" messages to file only
    * turn off certain log messages with minimal cpu impact
    * discard warning messages when running in production mode
    * log messages of type x|y|z to database tables x, y, z
    * throttle log messages if they start to overwhelm the system

"""


# helper imports
from ..helpers.debugging import smart_dotted_idpath
from mexceptionplus import reraiseplus
from mevent import Event

# python imports
import logging



class MewloLogManager(object):
    """
    MewloLogManager - the main supervisor class that manages a collection of Loggers
    """

    def __init__(self, debugmode):
        self.loggers = []
        self.debugmode = debugmode


    def startup(self, mewlosite, eventlist):
        """Startup everything, we are about to exit."""
        self.mewlosite = mewlosite
        for logger in self.loggers:
            logger.startup()


    def shutdown(self):
        """Shutdown everything, we are about to exit."""
        for logger in self.loggers:
            logger.shutdown()



    def set_debugmode(self, val):
        self.debugmode = val

    def add_logger(self, logger):
        """Just add a child logger to our collection."""
        self.loggers.append(logger)



    def process(self, logmessage):
        """Process a logmessage(Event), by allowing each of our attached loggers to handle it."""
        #print "PROCESSING MESSAGE "+str(logmessage)+ " for "+str(len(self.loggers))+" loggers."
        wrotecount = 0
        for logger in self.loggers:
            wrotecount += logger.process(logmessage, wrotecount)
        # if debug mode, and no one else handled it, print it
        if (wrotecount==0):
            if (self.debugmode):
                # echo it on screen if there are no loggers registered?
                if (False):
                    print str(logmessage)
        # return if true
        return wrotecount


    def hook_pythonlogger(self, pythonlogger_name, pythonlogger_level=logging.DEBUG):
        """Hook into python logging system to catch python error messages and create events from them for mewlo logging."""
        # ok get/create the logger, and set its log level
        pythonlogger = logging.getLogger(pythonlogger_name)
        pythonlogger.setLevel(pythonlogger_level)
        # now we add a handler that calls into us
        pythonloghandler = PythonLogHandler(self, pythonlogger_name)
        pythonlogger.addHandler(pythonloghandler)
        return pythonlogger



    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = " "*indent + "LogManager reporting in.\n"
        indent += 1
        #
        outstr += " "*indent + str(len(self.loggers)) + " loggers attached:\n"
        indent += 1
        for logger in self.loggers:
            outstr += logger.dumps(indent+1)
        return outstr








class MewloLogFilter(object):
    """
    MewloLogFilter - class responsible for deciding if a log message should be handled by a Logger; each logger has a list of zero or more LogFilters to check for match
    """

    def __init__(self):
        self.andfilters = []


    def startup(self):
        """Any initial startup to do?"""
        pass

    def shutdown(self):
        """Shutdown everything, we are about to exit."""
        pass


    def add_andfilter(self, filter):
        """Add a chained filter which is treated like an AND."""

        self.andfilters.append(filter)


    def doesmatch_full(self, logmessage, wrotecount):
        """Check if the logmessage matches our filter (or ALL of them if there are multiple chained with us."""

        # first check against ourself, if fail, then no point going any further
        if (not self.doesmatch_us(logmessage, wrotecount)):
            # doesn't match our condition
            return False
        # it matched us, now let's make sure it matches ALL of our AND filters (if any)
        if (not self.doesmatch_andchains(logmessage, wrotecount)):
            # doesn't match one of our registered AND chain of filters
            return False
        # it's good!
        return True



    def doesmatch_andchains(self, logmessage, wrotecount):
        """Check if logmessages matches any attached "AND" chained filters (we may have none)."""

        # test ALL and reject if any reject
        for filter in self.andfilters:
            if (not filter.doesmatch_full(logmessage, wrotecount)):
                return False
        # it matched ALL, so it's good
        return True



    def doesmatch_us(self, logmessage, wrotecount):
        """This is the exposed public function to check if a logmessage matches the filter. It will normally be implemented by a subclass."""

        # parent class just returns True so it will always match
        return True


    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = " "*indent + "MewloLogFilter (" + self.__class__.__name__  + ") reporting in.\n"
        indent += 1
        #
        if (len(self.andfilters)>0):
            outstr += " "*indent + str(len(self.andfilters)) + " and_filters attached:\n"
            indent += 1
            for andfilter in self.andfilters:
                outstr += andfilter.dumps(indent+1)
        return outstr






class MewloLogModifier(object):
    """MewloLogModifier - runs early and can modify/add stuff to log events before they are sent to a LogTarget."""
    # ATTN: We don't actually tie-in the MewloLogModifier yet to anything.

    def __init__(self):
        pass

    def modify_event(self, event):
        """Modify the event in-place."""
        pass



class MewloLogFormatter(object):
    """MewloLogFormatter - one and only one of these can be used to format a log string before writing it out to some file."""

    def __init__(self, formatstr=None):
        self.formatstr = formatstr

    def format_logmessage_as_string(self, logmessage):
        """Return a string which formates the event."""
        return logmessage.as_string()





class MewloLogTarget(object):
    """
    MewloLogTarget - targets for loggers; each logger has a list of LogTargets to perform on match
    """

    def __init__(self, logformatter=None):
        self.isenabled = True
        self.startedup = False
        self.logqueue = []
        self.logformatter = logformatter


    def set_isenabled(self, flagval):
        self.isenabled = flagval
    def get_isenabled(self):
        return self.isenabled


    def startup(self):
        """Any initial startup to do?"""
        self.startedup = True

    def shutdown(self):
        """Shutdown everything, we are about to exit."""
        self.flushqueue()
        # clear started up flag so people know we can't write to it anymore
        self.startedup = False


    def readytowrite(self):
        """Are we ready to write out stuff?"""
        return self.get_startedup()


    def set_logformatter(self, logformatter):
        self.logformatter = logformatter


    def process(self, logmessage):
        """Process the target action (write to file, save to database, emailing, etc.).  This should be overridden by subclass to do actual work."""
        print "Activating base LogTarget action, which is to write log message to screen: " + logmessage.dumps() + "\n"
        # return 1 to say it was written by target
        return 1

    def get_nicelabel(self):
        return self.__class__.__name__

    def get_startedup(self):
        return self.startedup


    def queuelog(self, logmessage):
        self.logqueue.append(logmessage)
        # ATTN: DISABLED FOR NOW
        pass

    def flushqueue(self):
        # process log queue
        if (self.readytowrite()):
            for logmessage in self.logqueue:
                self.process(logmessage, True)
            # clear it
            self.logqueue = []
        else:
            # we cannot flush queue -- should we error about this?
            if (len(self.logqueue)>0):
                print "ATTN: ERROR: In flushqueue for log target {0} and there are {1} queued messages to write, but we are not ready to write, so nothing was done.".format(self,len(self.logqueue))

    def get_queuelen(self):
        return len(self.logqueue)




    def process_or_queue(self, logmessage):
        """Process a line if we are ready, or queue it if not."""
        thiswrotecount = 0
        try:
            print "Considering target: "+str(self.get_nicelabel())+" with "+str(logmessage)
            if (self.readytowrite()):
                print "says ready to write."
                # target is ready to write -- but before we write we flush any pending queue
                if (self.get_queuelen()>0):
                    self.flushqueue()
                # send new message
                thiswrotecount += self.process(logmessage, False)
                #print "Sent to "+str(target)
            else:
                # send it to target queue
                print "queing not ready to write."
                self.queuelog(logmessage)
                #print "queud to log"
        except IOError as exp:
            # first thing we need to do is disable this target, in case we get recursively called or decide to keep running
            self.set_isenabled(False)
            # ATTN: todo
            # what should we do now? if we raise an exception here, we can't continue with the other targets
            # the best thing to do might be to LOG the error here (or add it to error list) and continue
            # raise a modified wrapper exception which can add some text info, to show who owns the object causing the exception to provide extra info
            # we probably wouldn't consider this a fatal error that should stop program from executing.
            reraiseplus(exp, "Disabling the logger where the error occurred: ", obj=self)
        # return items written
        return thiswrotecount





    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        logtargetlabel = self.get_nicelabel()
        outstr = " "*indent + "{0} reporting in.\n".format(logtargetlabel)
        return outstr








class MewloLogger(object):
    """
    MewloLogger - responsible for saving/writing a log event to some destination, and matching log events to decide whether to handle them.
    """


    def __init__(self, id):
        self.id = id
        #
        self.filters = []
        self.targets = []
        self.deferredmessages = []

    def get_id(self):
        return self.id


    def add_filter(self, filter):
        """Append a filter.  Multiple appended filters are treated like OR conditions (you can simulate AND by chaining filters together."""
        self.filters.append(filter)



    def add_target(self, target):
        """Append a target.  Targets will be run when the filters match. Multiple appended targets will be run in sequence."""
        self.targets.append(target)


    def startup(self):
        """Any initial startup stuff to do?"""
        for filter in self.filters:
            filter.startup()
        for target in self.targets:
            target.startup()


    def shutdown(self):
        """Shutdown everything, we are about to exit."""
        for filter in self.filters:
            filter.shutdown()
        for target in self.targets:
            # mark it as disabled so we won't call it again after this
            # note we do this here rather than in target class to avoid potential that derived target will forget to call this
            target.set_isenabled(False)
            # shut it down
            target.shutdown()



    def process(self, logmessage, wrotecount):
        """Process a logmessage(Event).  This may involve ignoring it if it doesn't match our filters, or sending it to Targets immediately if it does."""
        thiswrotecount = 0
        if (self.doesmatch_filters(logmessage, wrotecount)):
            thiswrotecount = self.run_targets(logmessage)
        else:
            print "LOGGER IS SKIPPING MESSAGE."
            pass
        return thiswrotecount



    def doesmatch_filters(self, logmessage, wrotecount):
        """Return True if this message matches ANY of the filter(s) for the logger.."""
        # if no filters added, then it's an automatic match
        if (len(self.filters) == 0):
            return True
        # see if any filter matches it
        for filter in self.filters:
            if (filter.doesmatch_full(logmessage, wrotecount)):
                return True
        # nothing matched, so it's false
        return False



    def run_targets(self, logmessage):
        """Run ALL registered targets on the message."""
        thiswrotecount = 0
        #print "ATTN: in run_targets with "+str(logmessage)
        for target in self.targets:
            #print "Considering target: "+str(target.get_nicelabel())
            if (target.get_isenabled()):
                thiswrotecount += target.process_or_queue(logmessage)
        return thiswrotecount


    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = " "*indent + "Logger '{0}' reporting in.\n".format(self.id)
        indent += 1
        #
        if (len(self.filters)>0):
            outstr += " "*indent + str(len(self.filters)) + " logfilters attached:\n"
            indent += 1
            for filter in self.filters:
                outstr += filter.dumps(indent+1)
        #
        if (len(self.targets)>0):
            outstr += " "*indent + str(len(self.targets)) + " logtargets attached:\n"
            indent += 1
            for target in self.targets:
                outstr += target.dumps(indent+1)
        #
        return outstr


















class PythonLogHandler(logging.Handler):
    """A custom log handler we use to route python log messages to the log manager."""

    def __init__(self, logmanager, label):
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        self.logmanager = logmanager
        self.label = label

    def emit(self, record):
        # record.message is the log message
        msg = self.format(record)
        level = record.levelname
        eventtype = Event.pythonlogginglevel_to_eventlevel(level)
        #
        event = Event({'msg':msg, 'type':eventtype, 'source':self.label})
        #print "EMITTING: "+msg
        self.logmanager.process(event)

