"""
mmessaging.py
This module defines classes that are used for user-2-user messaging.
We have 3 basic classes:
    * mboxfolder - lets system and users create custom folders
    * mboxin - small lightweight objects that represent a received message (but not the actual message content).
    * mboxout - actual sent messages with their contents; a single outgoing message can be sent to many recipients.
"""


# mewlo imports
from ..database import mdbmodel
from ..database import mdbfield
from ..database import mdbmixins
from ..manager import manager
from ..helpers import misc

# python imports






class MewloMboxFolder(mdbmodel.MewloDbModel):
    """The class that represents user mailboxes."""

    # class variables
    dbtablename = 'mboxfolder'
    dbschemaname = 'default'

    @classmethod
    def define_fields(cls, dbmanager):
        """This class-level function defines the database fields for this model -- the columns, etc."""

        # define fields list
        fieldlist = [

            mdbfield.DbfPrimaryId('id', {
                'label': "The primary key and id# for this row"
                }),

            mdbmixins.dbfmixin_gobreference('owner',"The user that owns this mbox folder (if NULL then everyone has it)"),

            mdbfield.DbfTypeString('foldertype', {
                'label': "The type of mbox folder"
                }),

            mdbfield.DbfLabelString('label', {
                'label': "The descriptive label for the folder"
                }),

            mdbfield.Dbf1toN_Right('parentfolder',  {
                'label': "The parent mbox folder",
                'leftclass': MewloMboxFolder,
                }),

             ]

        return fieldlist












class MewloMboxOut(mdbmodel.MewloDbModel):
    """The class that represents outgoing source messages."""

    # class variables
    dbtablename = 'mboxout'
    dbschemaname = 'default'

    @classmethod
    def define_fields(cls, dbmanager):
        """This class-level function defines the database fields for this model -- the columns, etc."""

        # define fields list
        fieldlist = [

            # standard primary id number field
            mdbfield.DbfPrimaryId('id', {
                'label': "The primary key and id# for this row"
                }),

            mdbmixins.dbfmixin_gobreference('sender', "The user who created/sent this message."),

            mdbfield.Dbf1toN_Right('folder',  {
                'label': "The containing sent-mail mbox folder",
                'leftclass': MewloMboxFolder,
                }),

            mdbfield.DbfTypeString('status',  {
                'label': "What is the status of this message (draft, sent, etc.)",
                }),
            mdbfield.DbfTimestamp('date_created',  {
                'label': "Date the messag was created",
                }),
            mdbfield.DbfTimestamp('date_sent',  {
                'label': "Date the message was sent (if at all)",
                }),

            mdbfield.Dbf1toN_Right('replyingto',  {
                'label': "The original incoming message that this message is a reply to",
                'leftclass': MewloMboxIn,
                'circular': True,
                }),

            mdbfield.DbfText('message_subject',  {
                'label': "Subject of the message",
                }),
            mdbfield.DbfText('message_body',  {
                'label': "Contents of the message",
                }),
            mdbfield.DbfText('recipient_string',  {
                'label': "String of recipients (will be parsed at time of sending)",
                }),

             ]

        return fieldlist







class MewloMboxIn(mdbmodel.MewloDbModel):
    """The LIGHTWEIGHT class that represents incoming messages."""

    # class variables
    dbtablename = 'mboxin'
    dbschemaname = 'default'

    @classmethod
    def define_fields(cls, dbmanager):
        """This class-level function defines the database fields for this model -- the columns, etc."""

        # define fields list
        fieldlist = [

            # standard primary id number field
            mdbfield.DbfPrimaryId('id', {
                'label': "The primary key and id# for this row"
                }),

            mdbmixins.dbfmixin_gobreference('recipient', "The user who has received this message"),

            mdbfield.Dbf1toN_Right('folder',  {
                'label': "The containing received mbox folder",
                'leftclass': MewloMboxFolder,
                }),

            mdbfield.Dbf1toN_Right('mboxout',  {
                'label': "The source (out) message",
                'leftclass': MewloMboxOut,
                }),

            mdbfield.DbfTimestamp('date_read',  {
                'label': "Date the messag was read (if at all)",
                }),

            mdbfield.DbfTypeString('notification_state',  {
                'label': "Was user notified about this new message (or do they have email notifications disabled)?",
                }),

             ]

        return fieldlist

