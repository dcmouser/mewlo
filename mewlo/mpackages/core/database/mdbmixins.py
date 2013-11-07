"""
mdbmodelmizins.py

This file contains some common model mixins to make it easier to add fields to a model.

"""


# helper imports
import mdbfield






class MewloDbModelMixin(object):
    """An object provides some mixin data for a model."""
    pass






class MewloDbModelMixin_UserAndTimestamp(MewloDbModelMixin):
    """An object provides some mixin data for a model."""

    @classmethod
    def get_dbfields(cls, prefixstr=''):
        """Mixin fields to help track authorship and modification info for an object."""
        # define field list
        fieldlist = [
            mdbfield.DbfForeignUserId(prefixstr+'userid', {
            #mdbfield.DbfInteger(prefixstr+'userid', {
                'label': "The {0}userid for this object".format(prefixstr)
                }),
            mdbfield.DbfUserIp(prefixstr+'userip', {
                'label': "The {0}ip for this object".format(prefixstr)
                }),
            mdbfield.DbfTimestamp(prefixstr+'timestamp', {
                'label': "The {0}timestamp for this object".format(prefixstr)
                }),
            ]
        return fieldlist







class MewloDbModelMixin_AuthorTracker(MewloDbModelMixin):
    """An object provides some mixin data for a model."""

    @classmethod
    def get_dbfields(cls, prefixstr=''):
        """Mixin fields for tracking author creation+modification data."""
        # define fields list
        fields_creation = MewloDbModelMixin_UserAndTimestamp.get_dbfields(prefixstr+'creation_')
        fields_modification = MewloDbModelMixin_UserAndTimestamp.get_dbfields(prefixstr+'modification_')
        fieldlist = fields_creation + fields_modification
        return fieldlist




class MewloDbModelMixin_Workflow(MewloDbModelMixin):
    """An object provides some mixin data for a model."""

    @classmethod
    def get_dbfields(cls, prefixstr=''):
        """Mixin fields for tracking author creation+modification data."""
        # define fields list
        fieldlist = [
            mdbfield.DbfBoolean(prefixstr+'is_deleted', {
                'label': "Has the object been virtually deleted?"
                }),
            mdbfield.DbfBoolean(prefixstr+'is_draft', {
                'label': "Has the object been marked as in draft state by author?"
                }),
            mdbfield.DbfEnum(prefixstr+'stage_workflow', {
                'label': "Workflow stage of the object"
                }),
            ]
        return fieldlist




