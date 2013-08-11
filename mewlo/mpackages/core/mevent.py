"""
mevent.py
This module contains classes and functions for custom event/error handling
"""


# helpers
from helpers.debugging import smart_dotted_idpath

# python modules
import sys
import traceback








class MewloEvent(object):
    """Base class for mewlo-specific event/error class."""

    # class constants
    DEF_ID_default = ''
    DEF_ID_failure = 'failure'
    DEF_LEVEL_default = 0
    DEF_ETYPE_warning = "WARNING"
    DEF_ETYPE_error = "ERROR"
    DEF_ETYPE_failure = "FAILURE"


    def __init__(self, etype = DEF_ETYPE_error, msg='', id=DEF_ID_default, level=DEF_LEVEL_default, obj=None, extra=None, exp=None):
        # init
        self.etype = etype
        self.msg = msg
        self.id = id
        self.level = level
        self.obj = obj
        self.extra = extra
        self.exp = exp
        #
        self.tracebac = None
        self.objtext = None
        self.exptext = None
        self.context = None
        #
        if (exp!=None):
            self.exptext = str(exp)


    def __str__(self):
        return self.stringify()


    def set_context(self, context):
        self.context = context

    def isetype(self, etype):
        """Check if etype matches."""
        # ATTN: we might later want to add a flag_iserror to events to distinguish the two "kinds" of things
        if (self.etype == etype):
            return True
        return False


    def stringify(self):
        retstr = "Event (%s) '%s' [ID:%s] Level %s" % (self.etype, self.msg, self.id, self.level)
        if (self.objtext!=None):
            retstr += " {OBJ: %s}" % smart_dotted_idpath(self.obj)
        if (self.extra!=None):
            retstr += " {EXTRA: %s}" % str(self.extra)
        if (self.exptext!=None):
            retstr += " {EXCEPTION: %s}" % str(self.exptext)
        if (self.context!=None):
            retstr += " {CONTEXT: %s}" % str(self.context)
        #
        return retstr












class MewloEventList(object):
    """Event tracker holds multiple events."""

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

    def set_context(self, context):
        self.context = context
    def add_context(self, context):
        if (self.context==None):
            self.context = context
        else:
            self.context.append(context)



    def add(self, event):
        """Just append a new event."""
        # if its None just ignore
        if (event==None):
            return
        # before we add it, we set it's context
        if (self.context!=None):
            event.set_context(self.context)
        # now add it
        self.events.append(event)





    def add_simple(self, msg, etype, id, exp=None):
        """Add a simple event."""
        # if msg is blank or '' then ignore
        if (msg==None or msg==''):
            return
        # if its already an event, just add it
        if (isinstance(msg, MewloEvent)):
            self.add(msg)
            return msg
        else:
            # create the event
            mevent = MewloEvent(etype, msg, id, exp=exp)
            # append it
            self.add(mevent)
            return mevent



    def add_simpleerror(self, msg, id=MewloEvent.DEF_ID_default):
        """Add a simple error."""
        return self.add_simple(msg, MewloEvent.DEF_ETYPE_error, id)


    def add_simplewarning(self, msg, id=MewloEvent.DEF_ID_default):
        """Add a simple warning."""
        return self.add_simple(msg, MewloEvent.DEF_ETYPE_warning, id)


    def add_simpleexception(self, exp, msg='', id=MewloEvent.DEF_ID_default):
        """Add an exception as an error."""
        return self.add_simpleerror(msg, id, exp=exp)



    def count_errors(self):
        """Shorthand to count the number of events of error type."""
        return self.count_byetype(MewloEvent.DEF_ETYPE_error)


    def count_byetype(self, etype):
        """Return a count of the number of events of the given type."""
        matchcount = 0
        for event in self.events:
            if (event.isetype(etype)):
                matchcount += 1
        # return count
        return matchcount




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







def MewloFailure(msg, exp=None, obj=None, id = MewloEvent.DEF_ID_failure, level=MewloEvent.DEF_LEVEL_default, extra=None):
    """Helper function to create error event"""
    mevent = MewloEvent(MewloEvent.DEF_ETYPE_failure, msg, id, level, obj, extra=extra, exp=exp)
    return mevent

