"""
mmailmanager.py
helper object for emailing
"""


# mewlo imports
from ..manager import manager

# python library imports
import pyzmail


class MewloMailManager(manager.MewloManager):
    """A helper object that handles all mail sending."""

    def __init__(self, mewlosite, debugmode):
        """Constructor."""
        super(MewloMailManager,self).__init__(mewlosite, debugmode)

    def startup(self, eventlist):
        super(MewloMailManager,self).startup(eventlist)
        # use site settings to configure mail settings

    def shutdown(self):
        super(MewloMailManager,self).shutdown()

    def sendemail(self, maildict):
        """Send a mail message."""
        pass


