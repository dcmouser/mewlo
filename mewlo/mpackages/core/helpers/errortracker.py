"""
This module defines classes and functions that help track errors and warnings in a given context.

Some things to think about:
    * Should we use proper classes for errors/warnings that can track error file/line, timestamp, dotted context path?
    * Should we worry about performance of using this class often?
    * Should we unify to using this class for ALL errors?
    * Should we use a MewloException class that owns this and handle all error reporting via raising exceptions?
    * Should we generalize over warnings/errors and simply use a dictionary of lists, with "error" and "warning" simply the common indices?

"""


class ErrorTracker(object):
    """
    The ErrorTracker class keeps simple list of errors and warnings, and includes support functions for adding and displaying them.
    """

    def __init__(self, errorstr=None, warningstr=None):
        """Constructor with optional arguements for initializing the object with starting error or warning string."""
        self.errorstrings = []
        self.warningstrings = []
        #
        self.add_errorstr(errorstr)
        self.add_warningstr(warningstr)


    def add_errorstr(self, astr):
        """Add an error string to the list."""
        if (astr==None or astr==""):
            return
        self.errorstrings.append(astr)


    def add_warningstr(self, astr):
        """Add a warning string to the list."""
        if (astr==None or astr==""):
            return
        self.warningstrings.append(astr)


    def joingerrors(self, joinstring=", "):
        """Return a string that is a comma separated join of all errors."""
        return joinstring.join(self.errorstrings)
    def counterrors(self):
        """Return a count of the number of errors."""
        return len(self.errorstrings)

    def joingwarnings(self, joinstring=", "):
        """Return a string that is a comma separated join of all warnings."""
        return joinstring.join(self.warningstrings)
    def countwarnings(self):
        """Return a count of the number of warnings."""
        return len(self.warningstrings)

    def tostring(self, joinstring=", "):
        """Return a string that is a comma separated join of all errors and warnings."""
        return joinstring.join(self.errorstrings + self.warningstrings)

    def countall(self):
        """Return a count of the number of warnings+errors."""
        return len(self.warningstrings)+len(self.errorstrings)

    def debug(self, indentstr=""):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = ""
        outstr += indentstr+"Errors:"
        if (len(self.errorstrings)==0):
            outstr += " None.\n"
        else:
            outstr += "\n"
            index = 0
            for astr in self.errorstrings:
                index += 1
                outstr += indentstr+" "+str(index)+". "+astr+"\n"
        #
        outstr += indentstr+"Warnings:"
        if (len(self.warningstrings)==0):
            outstr += " None.\n"
        else:
            outstr += "\n"
            index = 0
            for astr in self.warningstrings:
                index += 1
                outstr += indentstr+" "+str(index)+". "+astr+"\n"
        #
        return outstr
