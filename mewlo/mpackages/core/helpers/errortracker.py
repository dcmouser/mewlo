# errortracker.py
"""Support classes to help track errors related to an object"""

class ErrorTracker(object):

    def __init__(self, errorstr=None, warningstr=None):
        self.errorstrings = []
        self.warningstrings = []
        #
        self.add_errorstr(errorstr)
        self.add_warningstr(warningstr)


    def add_errorstr(self, astr):
        if (astr==None or astr==""):
            return
        self.errorstrings.append(astr)

    def add_warningstr(self, astr):
        if (astr==None or astr==""):
            return
        self.warningstrings.append(astr)

    def joingerrors(self):
        return ", ".join(self.errorstrings)
    def counterrors(self):
        return len(self.errorstrings)

    def joingwarnings(self):
        return ", ".join(self.warningstrings)
    def countwarnings(self):
        return len(self.warningstrings)

    def tostring(self):
        return ", ".join(self.errorstrings + self.warningstrings)


    def debug(self,indentstr=""):
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
        if (len(self.errorstrings)==0):
            outstr += " None.\n"
        else:
            outstr += "\n"
            index = 0
            for astr in self.warningstrings:
                index += 1
                outstr += indentstr+" "+str(index)+". "+astr+"\n"
        #
        return outstr
