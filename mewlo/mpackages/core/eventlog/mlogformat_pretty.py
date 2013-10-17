"""
mlogformat_pretty.py

Simple class that formats log events for nicer human readability

"""


# mewlo imports
import mlogger

# python imports
import time



class MewloLogFormatter_Pretty(mlogger.MewloLogFormatter):
    """MewloLogFormatter - one and only one of these can be used to format a log string before writing it out to some file."""

    def __init__(self, formatstr=None):
        super(MewloLogFormatter_Pretty,self).__init__(formatstr=formatstr)

    def format_logmessage_as_string(self, logmessage):
        """Return a string which formates the event."""
        outfields = {}
        for fieldkey in logmessage.fields.keys():
            if (fieldkey == 'timestamp'):
                val = time.ctime(logmessage.fields[fieldkey])
            else:
                val = logmessage.fields[fieldkey]
            outfields[fieldkey]=val
        return str(outfields)



