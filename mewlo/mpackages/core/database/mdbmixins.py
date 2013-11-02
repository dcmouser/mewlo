"""
mdbmodelmizins.py

This file contains some common model mixins.

"""


# helper imports
import mdbfield






class MewloDbModelMixin(object):
    """An object provides some mixin data for a model."""

    @classmethod
    def make_dbfields_userandtimestamp(cls, prefixstr):
        """Helper function to generate fields."""
        fieldlist = [
            mdbfield.DbfForeignUserId(prefixstr+'_userid', {
                'label': "The {0} userid for this object".format(prefixstr)
                }),
            mdbfield.DbfUserIp(prefixstr+'_userip', {
                'label': "The {0} ip for this object".format(prefixstr)
                }),
            mdbfield.DbfTimestamp(prefixstr+'_timestamp', {
                'label': "The {0} timestamp for this object".format(prefixstr)
                }),
            ]
        return fieldlist







class MewloDbModelMixin_AuthorTracker(MewloDbModelMixin):
    """An object provides some mixin data for a model."""

    @classmethod
    def get_dbfields(cls):
        """Mixin fields for tracking author creation+modification data."""
        # define fields list

        fields_creation = cls.make_dbfields_userandtimestamp('creation')
        fields_modification = cls.make_dbfields_userandtimestamp('modification')

        fieldlist = fields_creation + fields_modification

        return fieldlist




class MewloDbModelMixin_Workflow(MewloDbModelMixin):
    """An object provides some mixin data for a model."""

    @classmethod
    def get_dbfields(cls):
        """Mixin fields for tracking author creation+modification data."""
        # define fields list

        fieldlist = [
            mdbfield.DbfBoolean('is_deleted', {
                'label': "Has the object been virtually deleted?"
                }),
            mdbfield.DbfBoolean('is_draft', {
                'label': "Has the object been marked as in draft state by author?"
                }),
            mdbfield.DbfEnum('stage_workflow', {
                'label': "Workflow stage of the object"
                }),
            ]
        return fieldlist




