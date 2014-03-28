"""
mdbmodelmixins.py

This file contains some common model mixins to make it easier to add fields to a model.
We use these "mixins" as a way for us to add common fields, and sets of fields to models.

"""

# mewlo imports
import mdbfield





def dbfmixins_userandtimestamp(prefixstr=''):
    """Mixin fields to help track authorship and modification info for an object."""
    fieldlist = [
        mdbfield.DbfForeignUserId(prefixstr+'userid', {
            'label': "The {0}userid for this object".format(prefixstr)
            }),
        mdbfield.DbfServerIp(prefixstr+'userip', {
           'label': "The {0}ip for this object".format(prefixstr)
            }),
        mdbfield.DbfTimestamp(prefixstr+'timestamp', {
           'label': "The {0}timestamp for this object".format(prefixstr)
           }),
        ]
    return fieldlist




def dbfmixins_authortracker(prefixstr=''):
    """Mixin fields for tracking author creation+modification data."""
    fields_creation = dbfmixins_userandtimestamp(prefixstr+'creation_')
    fields_modification = dbfmixins_userandtimestamp(prefixstr+'modification_')
    fieldlist = fields_creation + fields_modification
    return fieldlist




def dbfmixins_workflow(prefixstr=''):
    """Mixin fields for tracking author creation+modification data."""
    fieldlist = [
        mdbfield.DbfBoolean(prefixstr+'is_draft', {
            'label': "Has the object been marked as in draft state by author?"
            }),
        mdbfield.DbfEnum(prefixstr+'stage_workflow', {
            'label': "Workflow stage of the object"
            }),
        ]
    return fieldlist




def dbfmixin_gobselfreference():
    """Mixin field for adding a global object id to a model."""
    import mdbmodel_gob
    fieldid = 'gobid'
    field = mdbfield.Dbf1to1_OneWay(fieldid, {
            'label': "The globally unique gob representing this object",
            'rightclass' : mdbmodel_gob.MewloDbModel_Gob,
            'relationname' : 'gob',
            })
    return field


def dbfmixin_gobreference(relationname, label):
    """Mixin field for referring to a global object id."""
    import mdbmodel_gob
    fieldid = relationname+"_gobid"
    field = mdbfield.Dbf1to1_OneWay(fieldid, {
            'label': "A reference to another {0} model via its globally unique id (gobid)".format(relationname),
            'rightclass' : mdbmodel_gob.MewloDbModel_Gob,
            'relationname' : relationname,
            })
    return field




def dbfmixins_disabledelete():
    """Mixin fields for tracking author creation+modification data."""
    fieldlist = [
        mdbfield.DbfBoolean('is_deleted', {
            'label': "Has the object been virtually deleted (invisible and unusable)?"
            }),
        mdbfield.DbfBoolean('is_disabled', {
            'label': "Has the object been disabled (but is still visible)?"
            }),
        mdbfield.DbfLabelString('disabledreason', {
            'label': "Reason the object is disabled (if it is)"
            }),
        ]
    return fieldlist




def dbfmixins_dateipuse():
    """Mixin fields for date created and last used and ip created and last used."""
    fieldlist = [
        mdbfield.DbfServerIp('ip_created', {
            'label': "IP used at creation"
            }),
        mdbfield.DbfServerIp('ip_lastuse', {
            'label': "IP of last use"
            }),
        mdbfield.DbfTimestamp('date_created', {
            'label': "Date of creation"
            }),
        mdbfield.DbfTimestamp('date_lastuse', {
            'label': "Date of last use"
            }),
        ]
    return fieldlist



