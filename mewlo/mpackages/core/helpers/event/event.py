"""
event.py
This module contains classes and functions for custom event/error handling
"""


# mewlo imports
from mewlo.mpackages.core.mexception import compute_traceback_astext

# helper imports
from mewlo.mpackages.core.helpers.debugging import smart_dotted_idpath

# python imports
import sys
import traceback








class Event(object):
    """Base class for event/error class."""

    # class constants
    DEF_SAFE_FIELDNAME_LIST = ["type","msg","exp","request","traceback","statuscode"]
    #
    DEF_ETYPE_failure = "FAILURE"
    DEF_ETYPE_error = "ERROR"
    DEF_ETYPE_warning = "WARNING"
    DEF_ETYPE_exception = "EXCEPTION"


    def __init__(self, fields=None, defaultfields = None):
        """Constructor for an Event.  We use a generic fields dictionary to specify all fields for the event, whose values overide an optional defaultfields dictionary. """
        # start with default fields
        if (defaultfields!=None):
            self.fields = dict(defaultfields)
        else:
            self.fields = {}
        # merge in fields
        if (fields != None):
            self.fields.update(fields)
        # check field safety?
        self.safetycheck_fields(self.fields)


    def __str__(self):
        return self.stringify()



    def setfield(self, fieldname, fieldval):
        self.fields[fieldname] = fieldval
        # check field safety?
        self.safetycheck_fieldname(fieldname)

    def getfield(self, fieldname, defaultval = None):
        if (fieldname in self.fields):
            return self.fields[fieldname]
        return defaultval


    def mergefields(self, fields):
        """Merge in new fields over existing, taking care of cases where one or both fields are None."""
        if (fields!=None):
            self.fields.update(fields)
            # check field safety?
            self.safetycheck_fields(fields)

    def mergemissings(self, fields):
        """Merge in missing fields."""
        for fieldname in fields.keys():
            if (not fieldname in self.fields) or (self.fields[fieldname]==None):
                self.fields[fieldname] = fields[fieldname]
                # check field safety?
                self.safetycheck_fieldname(fieldname)


    def fieldmatches(self, fieldname, fieldval):
        """Check if etype matches."""
        ourval = self.getfield(fieldname)
        if (ourval==fieldval):
            return True
        # if fieldval is a container (list), then return true if ourval is in the list
        try:
            if (ourval in fieldval):
                return True
        except:
            pass
        return False


    def safetycheck_fieldname(self, fieldname):
        """
        Check to make sure this is an allowed fieldname -- helps to catch coding typo errors
        ATTN: disable on optimization.
        """
        if (not fieldname in Event.DEF_SAFE_FIELDNAME_LIST):
            if (not fieldname.startswith("custom_")):
                raise Exception("Fieldname specified for Event [%s] that is not in our list of safe fieldnames (%s) and does not begin with 'custom_'." % (fieldname , ",".join(Event.DEF_SAFEFIELDNAMELIST)))

    def safetycheck_fields(self, fields):
        """
        Check to make sure fields are allowed fieldnames -- helps to catch coding typo errors
        ATTN: disable on optimization.
        """
        for fieldname in fields.keys():
            self.safetycheck_fieldname(fieldname)


    def stringify(self):
        """Return nice formatted string representation of event."""
        retstr = "Event " + str(self.fields)
        #
        return retstr


    def as_logline(self):
        return self.stringify()



    @classmethod
    def calc_traceback_text(cls):
        """Class function to get current stack traceback as text.  Used when creating an event from an exception."""
        exc_info = sys.exc_info()
        exceptiontype = exc_info[0]
        exceptionvalue = exc_info[1]
        traceback_object = exc_info[2]

        retstr = compute_traceback_astext(traceback_object,True)
        return retstr







class EventList(object):
    """Event list holds multiple events and provides some helper functions for working with multiple events."""

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



    def set_context(self, context):
        self.context = context

    def add_context(self, context):
        """Add context value to current context as dotted string path."""
        if (self.context==None):
            self.context = context
        else:
            self.context.append("."+context)



    def add(self, event):
        """Just append a new event."""
        # if its None just ignore
        if (event==None):
            return
        # before we add it, we set it's context
        if (self.context!=None):
            event.setfield("context",self.context)
        # now add it
        self.events.append(event)





    def add_simple(self, msg, fields=None):
        """Add a simple event."""
        # if msg is blank or '' then ignore
        if (msg==None or msg==''):
            return
        # if its already an event, just merge in any new overiding fields and add it; this can be useful if we have an Event (like a return failure code) and we want to add it to an Event list with extra info
        if (isinstance(msg, Event)):
            msg.mergefields(fields)
            self.add(msg)
            return msg
        else:
            # create the event
            mevent = Event(msg, fields)
            # append it
            self.add(mevent)
            return mevent



    def countfieldmatches(self, fieldname, fieldval):
        """Count matches of a field."""
        matchcount = 0
        for event in self.events:
            if (event.fieldmatches(fieldname, fieldval)):
                matchcount += 1
        # return count
        return matchcount


    def count_errors(self):
        """Shorthand to count the number of events of error type."""
        return self.countfieldmatches("type", Event.DEF_ETYPE_error)



    def stringify(self, indentstr=''):
        """Return a string that is a comma separated join of all events, regardless of type."""
        outstr = ""
        outstr += indentstr+"Events:"
        if (len(self)==0):
            outstr += " None.\n"
        else:
            outstr += "\n"
            index = 0
            for event in self.events:
                index += 1
                astr = str(event)
                outstr += indentstr+" "+str(index)+". "+astr+"\n"
        return outstr




    def debug(self, indentstr=''):
        return self.stringify(indentstr)








# These are shortcut helper functions

def EFailure(msg=None, fields=None):
    """Helper function to create failure type event"""
    defaultfields = { "msg":msg, "type":Event.DEF_ETYPE_failure }
    # create event
    return Event(fields, defaultfields)

def EError(msg=None, fields=None):
    """Helper function to create error type event"""
    defaultfields = { "msg":msg, "type":Event.DEF_ETYPE_error }
    # create event
    return Event(fields, defaultfields)

def EWarning(msg=None, fields=None):
    """Helper function to create warning type event"""
    defaultfields = { "msg":msg, "type":Event.DEF_ETYPE_warning }
    # create event
    return Event(fields, defaultfields)

def EException(msg=None, exp=None, fields=None, flag_traceback=True):
    """Helper function to create exception type event with full exception traceback info."""
    defaultfields = { "msg":msg, "type":Event.DEF_ETYPE_exception, "exp":exp }
    # add traceback?
    if (flag_traceback):
        defaultfields["traceback"] = Event.calc_traceback_text()
    # create event
    return Event(fields, defaultfields )



