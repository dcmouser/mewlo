# errortracker.py
"""Support classes to help track errors related to an object"""

class ErrorTracker(object):

    def __init__(self, initialerrorstr=None):
        self.errorstrings = []
        if (initialerrorstr != None):
            self.add_errorstring(initialerrorstr)


    def add_errorstring(self,errorstr):
        self.errorstrings.append(errorstr)

    def tostring(self):
        return ", ".join(self.errorstrings)

    def count(self):
        return len(self.errorstrings)


    def debug(self,indentstr=""):
        outstr = indentstr+"Last errors:"
        if (len(self.errorstrings)==0):
            outstr += " None."
        else:
            index = 0
            for errorstr in self.errorstrings:
                index += 1
                outstr += "\n"+indentstr+" "+str(index)+". "+errorstr
        return outstr
