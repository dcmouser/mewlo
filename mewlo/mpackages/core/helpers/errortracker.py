# errortracker.py
"""Support classes to help track errors related to an object"""

class ErrorTracker(object):

    def __init__(self):
        self.errorstrings = []


    def add_errorstring(self,errorstr):
        self.errorstrings.append(errorstr)


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
