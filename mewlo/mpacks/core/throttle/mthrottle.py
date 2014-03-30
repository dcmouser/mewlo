"""
mthrottle.py
This module defines the MewloThrottle class which is used to gracefully react to degenerate things that may happen too frequently.
For example, the throttle system can detect too many error emails being sent out, and throttle down such events, etc.
"""


# mewlo imports
from ..database import mdbmodel
from ..database import mdbfield
from ..database import mdbmixins
from ..manager import manager
from ..helpers import misc

# python imports






class MewloThrottleEvent(mdbmodel.MewloDbModel):
    """The MewloThrottleEvent class manages lightweight tracking of occurences so that behaviors can be throttled if they become excessive."""

    # class variables
    dbtablename = 'throttle_event'
    dbschemaname = 'default'

    @classmethod
    def define_fields(cls, dbmanager):
        """This class-level function defines the database fields for this model -- the columns, etc."""

        # define fields list
        fieldlist = [

            mdbfield.DbfPrimaryId('id', {
                'label': "The primary key and id# for this row"
                }),
            mdbfield.DbfTypeString('activity', {
                'label': "The name of the activity being throttled"
                }),
            mdbfield.DbfInteger('objectid', {
                'label': "Generic object id"
                }),
            mdbfield.DbfTimestamp('date', {
                'label': "The date timestamp of the event"
                }),
             ]

        return fieldlist








class MewloThrottleTrigger(mdbmodel.MewloDbModel):
    """The MewloThrottleTrigger class manages possible throttle triggers that have been activated due to excessive behavior."""

    # class variables
    dbtablename = 'throttle_trigger'
    dbschemaname = 'default'

    @classmethod
    def define_fields(cls, dbmanager):
        """This class-level function defines the database fields for this model -- the columns, etc."""

        # define fields list
        fieldlist = [

            mdbfield.DbfPrimaryId('id', {
                'label': "The primary key and id# for this row"
                }),
            mdbfield.DbfTypeString('activity', {
                'label': "The name of the activity being throttled"
                }),
            mdbfield.DbfInteger('objectid', {
                'label': "Generic object id"
                }),

            mdbfield.DbfBoolean('is_engaged', {
                'label': "Is this throttle trigger engaged"
                }),
            mdbfield.DbfTimestamp('date_triggered', {
                'label': "The date timestamp when the throttle was triggered"
                }),
            mdbfield.DbfTimestamp('date_updated', {
                'label': "The date timestamp when we last checked if the throttle should trigger"
                }),
             ]

        return fieldlist
