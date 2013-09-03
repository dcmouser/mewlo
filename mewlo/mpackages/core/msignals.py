"""
msignals.py
This module contains classes and functions for the signal sending/receiving system.
"""


# helper imports
from helpers.signals.signals import SignalDispatcher, SignalReceiver

# python imports





class MewloSignalDispatcher(SignalDispatcher):
    """The derived signal dispatcher."""

    def __init__(self, mewlosite):
        """Constructor."""
        # partent constructor
        super(MewloSignalDispatcher, self).__init__()
        # init
        self.mewlosite = mewlosite













class MewloSignalReceiver(SignalReceiver):
    """The object receives signals from dispatcher."""

    def __init__(self, mewlosite, callback, idfilter, sourcefilter, extra = None, flag_returnsvalue = True):
        """Constructor."""
        # partent constructor
        super(MewloSignalReceiver, self).__init__(callback, idfilter, sourcefilter, extra, flag_returnsvalue)
        # init
        self.mewlosite = mewlosite


