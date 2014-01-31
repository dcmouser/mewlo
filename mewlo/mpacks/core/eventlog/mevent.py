"""
mevent.py
This module contains classes and functions for custom event/error handling.

We use this Event class to store data associated with an event/error/warning/etc, and to write such events out to a log file or database log.

There are some alternatives for how we might represent the data associated with an Event class.

One alternative would be to define lots of specific separate member properties for all (most) fields we may want to record.
This would be the classic OOP method.
The advantage is better ability to typecheck fields, less possibility of errors in specifying or missing fields, better function all error checking.
A disadvantage is that there are a lot of potential fields, it may get a bit messy to have a member property for each one.

The other alternative would be to allow event fields to be open ended, specified as a dictionary.
The advantage is greater flexibility in adding fields, and easier support of lots of fields.
If we think we might have to support an "other" dictionary of arbitrary properties, then might be simpler to just have everything be in that dictionary.
This gives us a unified way of representing fields in a dictionary.

We chose to use the second alternative.  All event fields are represented in a single dictionary.

In order to support better error checking, we have a (possibly optional and turned off for performance) validation function to make sure the field values are valid.

About saving events and their fields: There are cases where we are not logging events to a target with a fixed set of columns.
In such cases we don't have to worry about arbitrary or unexpected fields, and a web application can invent it's own field property names.
However, in a more traditional target, writing to a database table, each field corresponds to a column, and most database engines will not allow us to add arbitrary field columns.
So we must decide how we want to handle such cases.  There are two separate issues we can consider.  First, we must consider how the columns are defined/decided.
And second we must decide how to handle fields which don't have a dedicated database column.
Our approach will be as follows:  Database target loggers will specify a mapping from event fields to columns, a list of fields to discard, and then an optional generic text column which will serialize any other fields.

Official Fields (not all will be in every event):
    type: FAILURE | ERROR | WARNING | EXCEPTION
    msg: Full text of the event messsage (can be arbitrarily long and contain newlines)
    exp: Exception object related to the event
    request: The MewloRequest object associated with the event (note the request object contains the response object)
    traceback: The traceback object associated with the event
    statuscode: The http status code associated with an error (we might later want to remove this and just pass request object and let logger grab statuscode from request response)
    loc: A dictionary containing keys [filename,lineno,function_name] of the event; support functions for adding events can grab this info automatically from callstack

"""



# python imports
import sys
import logging
import time





class Event(object):
    """Base class for event/error class."""

    # class constants
    #
    DEF_SAFE_FIELDNAME_LIST = ['type', 'msg', 'exp', 'request', 'traceback', 'statuscode', 'loc', 'source', 'timestamp']
    #
    DEF_ETYPE_debug = 'DEBUG'
    DEF_ETYPE_info = 'INFO'
    DEF_ETYPE_warning = 'WARNING'
    DEF_ETYPE_error = 'ERROR'
    DEF_ETYPE_critical = 'CRITICAL'
    #
    DEF_ETYPE_failure = 'FAILURE'
    DEF_ETYPE_exception = 'EXCEPTION'
    #
    DEF_ETYPE_PYTHONLOGGING_MAP = {
        'DEBUG' : logging.DEBUG,
        'INFO' : logging.INFO,
        'WARNING' : logging.WARNING,
        'ERROR' : logging.ERROR,
        'CRITICAL' : logging.ERROR,
        'FAILURE' : logging.ERROR,
        'EXCEPTION' : logging.ERROR,
        }
    DEF_ETYPE_PYTHONLOGGING_REVERSEMAP = {
        logging.DEBUG : 'DEBUG',
        logging.INFO : 'INFO',
        logging.WARNING : 'WARNING',
        logging.ERROR : 'ERROR'
        }
    #
    flag_safetycheckfields = True


    def __init__(self, fields=None, defaultfields=None):
        """Constructor for an Event.  We use a generic fields dictionary to specify all fields for the event, whose values overide an optional defaultfields dictionary. """
        # start with default fields (note we COPY it)
        if (defaultfields != None):
            self.fields = dict(defaultfields)
        else:
            self.fields = {}
        # force timestamp
        self.fields['timestamp'] = time.time()
        # merge in fields
        if (fields != None):
            self.fields.update(fields)
        # check field safety?
        self.safetycheck_fields(self.fields)


    def __str__(self):
        return self.stringify()

    def add_msgprefix(self, prefixstr):
        # add prefix to exsting message
        self.setfield('msg', prefixstr+self.getfield('msg',''))


    def setfield(self, fieldname, fieldval):
        self.fields[fieldname] = fieldval
        # check field safety?
        self.safetycheck_fieldname(fieldname)

    def getfield(self, fieldname, defaultval = None):
        if (fieldname in self.fields):
            return self.fields[fieldname]
        return defaultval


    def makecopy(self):
        return Event(self.fields)


    def mergefields(self, fields):
        """Merge in new fields over existing, taking care of cases where one or both fields are None."""
        if (fields != None):
            self.fields.update(fields)
            # check field safety?
            self.safetycheck_fields(fields)


    def mergemissings(self, fields):
        """Merge in missing fields."""
        for key,val in fields.iteritems():
            if (not key in self.fields) or (self.fields[key] == None):
                self.fields[key] = val
                # check field safety?
                self.safetycheck_fieldname(key)


    def fieldmatches(self, fieldname, fieldval):
        """Check if etype matches."""
        ourval = self.getfield(fieldname)
        if (ourval == fieldval):
            return True
        # if fieldval is a container (list), then return true if ourval is in the list
        # ATTN: is there a better way to do this with better performance
        try:
            if (ourval in fieldval):
                return True
        except:
            pass
        # didn't match
        return False


    def safetycheck_fieldname(self, fieldname):
        """
        Check to make sure this is an allowed fieldname -- helps to catch coding typo errors
        ATTN: disable on optimization.
        """
        if (not self.flag_safetycheckfields):
            return
        if (not fieldname in Event.DEF_SAFE_FIELDNAME_LIST):
            if (not fieldname.startswith('custom_')):
                raise Exception("Fieldname '{0}' specified for an Event that is not in our list of safe fieldnames [{1}] and does not begin with 'custom_'.".format(fieldname , ",".join(Event.DEF_SAFE_FIELDNAME_LIST)))

    def safetycheck_fields(self, fields):
        """
        Check to make sure fields are allowed fieldnames -- helps to catch coding typo errors
        ATTN: we should disable this on optimization.
        """
        if (self.flag_safetycheckfields):
            return
        for key in fields.keys():
            self.safetycheck_fieldname(key)


    def stringify(self):
        """Return nice formatted string representation of event."""
        retstr = "Event " + str(self.fields)
        return retstr


    def as_string(self):
        """
        Return the event string as it should be formatted for saving to log file.
        ATTN: we probably don't want the EVENT to decide this -- rather the log target, etc.
        """
        return self.stringify()


    def calc_pythonlogginglevel(self):
        """
        We sometimes want to write out an event as a log message to python logger; in that case we need a logging level.
        Python logging levels are:
            DEBUG 	Detailed information, typically of interest only when diagnosing problems.
            INFO 	Confirmation that things are working as expected.
            WARNING 	An indication that something unexpected happened, or indicative of some problem in the near future (e.g. ?disk space low?). The software is still working as expected.
            ERROR 	Due to a more serious problem, the software has not been able to perform some function.
            CRITICAL 	A serious error, indicating that the program itself may be unable to continue running.
        """
        etype = self.getfield('type')
        if (etype in Event.DEF_ETYPE_PYTHONLOGGING_MAP):
            pythonlevel = Event.DEF_ETYPE_PYTHONLOGGING_MAP[etype]
        else:
            pythonlevel = logging.ERROR
        return pythonlevel

    @classmethod
    def pythonlogginglevel_to_eventlevel(cls, pythonlevel):
        """Convert from a python logging level to our internal mewlo level."""
        if (pythonlevel in Event.DEF_ETYPE_PYTHONLOGGING_REVERSEMAP):
            eventlevel = Event.DEF_ETYPE_PYTHONLOGGING_REVERSEMAP[pythonlevel]
        else:
            eventlevel = Event.DEF_ETYPE_info
        return eventlevel



    @classmethod
    def calc_traceback_text(cls):
        """Class function to get current stack traceback as text.  Used when creating an event from an exception."""
        # let debugging cuntion do this for us
        from ..helpers import debugging
        return debugging.compute_traceback_astext()































class EventList(object):
    """Event list holds multiple events and provides some helper functions for working with multiple events."""
    # ATTN: Do we really need a custom list type for this?
    # ATTN: If so, let's at least make it derive from list?

    def __init__(self):
        # init
        self.events = []
        self.context = None


    def __str__(self):
        return self.stringify()

    def __getitem__(self, key):
        return self.events[key]

    def __len__(self):
        return len(self.events)

    def __iter__(self):
        return iter(self.events)


    def clear(self):
        self.events = []


    def set_context(self, context):
        """Set context value -- useful when generating lots of events that all have same parent-set context."""
        self.context = context

    def add_context(self, context):
        """Add context value to current context as dotted string path."""
        if (self.context == None):
            self.context = context
        else:
            self.context.append('.' + context)




    def append(self, event):
        """Just append a new event."""
        # if its None just ignore
        if (event == None):
            return
        # before we add it, we set it's context, iff one exists in event list
        if (self.context != None):
            event.setfield('context', self.context)
        # now add it
        self.events.append(event)


    def appendlist(self, eventlist):
        if (eventlist==None):
            return
        for event in eventlist:
            self.append(event)

    def mergefields_allevents(self, fields):
        for event in self.events:
            event.mergefields(fields)

    def makecopy(self):
        eventlist = EventList()
        for event in self.events:
            eventlist.append(event.makecopy())
        return eventlist



    def add_simple(self, msg, fields=None):
        """Add a simple event -- either from a string msg OR an existing event, which we modify."""
        # if msg is blank or '' then ignore
        if (msg == None or msg == ''):
            return
        # if its already an event, just merge in any new overiding fields and add it; this can be useful if we have an Event (like a return failure code) and we want to add it to an Event list with extra info
        if (isinstance(msg, Event)):
            msg.mergefields(fields)
            self.append(msg)
            return msg
        else:
            # create the event
            event = Event(msg, fields)
            # append it
            self.append(event)
            return event



    def countfieldmatches(self, fieldname, fieldval):
        """Count the number of events that have a matching fieldvalue -- useful for example for counting number of events of type ERROR."""
        matchcount = 0
        for event in self.events:
            if (event.fieldmatches(fieldname, fieldval)):
                matchcount += 1
        # return count
        return matchcount


    def count_errors(self):
        """Shorthand to count the number of events of error type."""
        return self.countfieldmatches('type', [Event.DEF_ETYPE_error, Event.DEF_ETYPE_failure])



    def stringify(self, indent=0):
        """Return a string that is a comma separated join of all events, regardless of type.  Useful for quick debugging."""
        outstr = ""
        outstr += " "*indent + "Events:"
        if (len(self) == 0):
            outstr += " None.\n"
        else:
            outstr += "\n"
            index = 0
            indent += 1
            for event in self.events:
                index += 1
                astr = str(event)
                outstr += " "*indent + str(index) + ". " + astr + "\n"
        return outstr



    def dumps(self, indent=0):
        return self.stringify(indent)


























# These are shortcut helper functions
# These are capitalized functions because they act like object constructors, and are designed to be concise highly visible ways to create error/events
# ATTN: todo -- refactor these to use args,kargs to simplify them?


def EFailure(msg="", fields=None, obj=None, flag_loc=False, calldepth=0):
    """Helper function to create failure type event"""
    return SimpleEventBuilder(msg, fields, obj, flag_loc, calldepth+1, {'type': Event.DEF_ETYPE_failure })

def EError(msg="", fields=None, obj=None, flag_loc=False, calldepth=0):
    """Helper function to create error type event"""
    return SimpleEventBuilder(msg, fields, obj, flag_loc, calldepth+1, {'type': Event.DEF_ETYPE_error })

def EWarning(msg="", fields=None, obj=None, flag_loc=False, calldepth=0):
    """Helper function to create warning type event"""
    return SimpleEventBuilder(msg, fields, obj, flag_loc, calldepth+1, {'type': Event.DEF_ETYPE_warning })

def EDebug(msg="", fields=None, obj=None, flag_loc=False, calldepth=0):
    """Helper function to create debug type event"""
    return SimpleEventBuilder(msg, fields, obj, flag_loc, calldepth+1, {'type': Event.DEF_ETYPE_debug })

def EInfo(msg="", fields=None, obj=None, flag_loc=False, calldepth=0):
    """Helper function to create debug type event"""
    return SimpleEventBuilder(msg, fields, obj, flag_loc, calldepth+1, {'type': Event.DEF_ETYPE_info })




def EException(msg="", exp=None, fields=None, flag_traceback=True, obj=None, flag_loc = True, calldepth=0):
    """Helper function to create exception type event with full exception traceback info."""
    # default fields
    defaultfields = { 'type': Event.DEF_ETYPE_exception, 'exp': exp }
    # add traceback?
    if (flag_traceback):
        defaultfields['traceback'] = Event.calc_traceback_text()
    # create event
    return SimpleEventBuilder(msg, fields, obj, flag_loc, calldepth+1, defaultfields)



def EFailureExtend(failure, msg="", fields=None, obj=None, flag_loc=False, calldepth=0):
    """Helper function to create failure type event by extending another"""
    if (isinstance(failure, Event)):
        # add the simple message of the other failure event
        addmsg = failure.getfield('msg', "")
    else:
        # assume previous failure is stringifyable and add that
        addmsg = str(failure)
    if (addmsg != ""):
        msg += " " + addmsg
    # build it
    return SimpleEventBuilder(msg, fields, obj, flag_loc, calldepth+1, {'type': Event.DEF_ETYPE_failure })



def SimpleEventBuilder(msg, fields, obj, flag_loc, calldepth, defaultfields):
    """Internal func. Helper function to create failure type event"""
    from ..helpers import debugging
    # add obj info
    if (obj != None):
        msg += debugging.smart_dotted_idpath(obj)
    # add message
    defaultfields['msg'] = msg
    # extra stuff?
    if (flag_loc):
        defaultfields['loc'] = debugging.calc_caller_dict(calldepth+1)
    # create event
    return Event(fields, defaultfields)
