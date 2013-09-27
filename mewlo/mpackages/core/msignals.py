"""
msignals.py
This module contains classes and functions for the signal sending/receiving system.
"""


# helper imports
from helpers.signals.signals import SignalDispatcher, SignalReceiver

# python imports





class MewloSignalDispatcher(SignalDispatcher):
    """The derived signal dispatcher."""

    def __init__(self):
        """Constructor."""
        # partent constructor
        super(MewloSignalDispatcher, self).__init__()


    def startup(self, eventlist):
        """Any startup stuff to do?"""
        pass

    def shutdown(self):
        """Any shutdown stuff to do?"""
        pass











class MewloSignalReceiver(SignalReceiver):
    """The object receives signals from dispatcher."""

    def __init__(self, callback, idfilter, sourcefilter, extra = None, flag_returnsvalue = True):
        """Constructor."""
        # partent constructor
        super(MewloSignalReceiver, self).__init__(callback, idfilter, sourcefilter, extra, flag_returnsvalue)



