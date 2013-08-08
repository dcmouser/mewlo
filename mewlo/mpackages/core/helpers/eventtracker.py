"""
eventtracker.py
This module defines classes and functions that help track errors and warnings in a given context.

Some things to think about:
    * Should we use proper classes for errors/warnings that can track error file/line, timestamp, dotted context path?
    * Should we worry about performance of using this class often?
    * Should we unify to using this class for ALL errors?
    * Should we use a MewloException class that owns this and handle all error reporting via raising exceptions?
    * Should we generalize over warnings/errors and simply use a dictionary of lists, with "error" and "warning" simply the common indices?

"""


class EventTracker(object):
    """
    The EventTracker class keeps simple list of errors and warnings, and includes support functions for adding and displaying them.
    """

    # event types
    DEF_TYPE_Warning = "WARNING"
    DEF_TYPE_Error = "ERROR"


    def __init__(self):
        """Constructor fpr event tracker."""
        self.events = []


    def warning(self, mesg, event={}):
        """Add a warning string to the list."""
        self.add_message_with_type(etype=self.DEF_TYPE_Warning, mesg=mesg, event=event)


    def error(self, mesg, event={}):
        """Add an error string to the list."""
        self.add_message_with_type(etype=self.DEF_TYPE_Error, mesg=mesg, event=event)



    def add_message_with_type(self, etype, mesg, event={}):
        """Add an event from a message and type."""
        # create dictionary for event
        newevent = dict(event)
        newevent['type']=etype
        newevent['mesg']=mesg
        # add it
        self.add_event(newevent)



    def add_event(self, event):
        """Add an event to the list."""
        self.events.append(event)



    def count_all(self):
        """Return a count of ALL events (errors+warnings+other)."""
        return len(self.events)


    def count_bytype(self, etype):
        """Return a count of events of the specified typestring."""
        foundcount = 0
        for event in self.events:
            if (event['type']==etype):
                foundcount+=1
        return foundcount


    def count_errors(self):
        """Return a count of the number of errors."""
        return self.count_bytype(etype=self.DEF_TYPE_Error)




    def tostring(self, etype='*', indentstr=''):
        """Return a string that is a comma separated join of all events, regardless of type."""
        outstr = ""
        outstr += indentstr+"Events:"
        if (len(self.events)==0):
            outstr += " None.\n"
        else:
            outstr += "\n"
            index = 0
            for event in self.events:
                if (etype=='*' or etype==event['type']):
                    index += 1
                    astr = self.event_to_string(event)
                    outstr += indentstr+" "+str(index)+". "+astr+"\n"
        return outstr



    def event_to_string(self, event):
        """Return a string describing the event."""
        return str(event)



    def debug(self, indentstr=""):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        return self.tostring(etype='*', indentstr=indentstr)

