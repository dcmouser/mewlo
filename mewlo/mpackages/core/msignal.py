"""
msignal.py
This module contains classes and functions for the signal sending/receiving system.
"""


# helper imports
from helpers.signal.signal import SignalDispatcher, SignalReceiver

# python imports





class MewloSignalDispatcher(SignalDispatcher):
    """The derived signal dispatcher."""

    def __init__(self):
        """Constructor."""
        # partent constructor
        super(MewloSignalDispatcher, self).__init__()


    def startup(self, mewlosite, eventlist):
        self.mewlosite = mewlosite
        # parent func
        super(MewloSignalDispatcher, self).startup()

    def shutdown(self):
        # parent func
        super(MewloSignalDispatcher, self).shutdown()








class MewloSignalReceiver(SignalReceiver):
    """The object receives signals from dispatcher."""

    def __init__(self, owner, callback, idfilter, sourcefilter, extra = None, flag_returnsvalue = True):
        """Constructor."""
        # partent constructor
        super(MewloSignalReceiver, self).__init__(owner, callback, idfilter, sourcefilter, extra, flag_returnsvalue)



