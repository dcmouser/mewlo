"""
mdbmodel_log.py

This is a base class for logging to database.
Subclasses can add new fields.

ATTN: We implement here some serialized support functions but they shouldnt be here, they should be more generically implemented in model or field class.

"""


# mewlo imports
import mdbmodel
import mdbfield
import mdbmixins

# python imports






class MewloDbModel_Log(mdbmodel.MewloDbModel):
    """Database model where each row is a serialized dictioary setting."""

    # class variables
    dbtablename = 'log'
    dbschemaname = 'default'

    # fields to ignore and not write out to database
    ignored_logfields = []


    def __init__(self):
        # initialize when creating manually
        self.extrafields_serialized = None




    # all of thes serialization functions should be done away with and handled transparently by a serialized field type


    def set_extrafields_dict(self, fields):
        """Serialize an object into the extrafields_serialized property."""
        self.extrafields_serialized = self.serialize_forstorage(fields)


    def set_property_byname(self, propname, propval):
        """Set an object property by name."""
        setattr(self, propname, propval)


    def map_dict_to_properties(self, dict):
        """Store dictionary 'dict' into the object's existing defined fields, and any fields that don't match, serialize into extrafields_serialized."""
        extrafields = {}
        fieldids = self.fieldhash.keys()
        # walk properties in dictionary and set object properties and extrafields dictionary
        for key,val in dict.iteritems():
            if (key in fieldids):
                # ok there is a field for this, so just save it
                self.set_property_byname(key, val)
            else:
                # ok we don't have a field for it
                if (key not in self.ignored_logfields):
                    # add it to our extra fields dictionary to serialize
                    extrafields[key] = val
        # handle extrafields
        if (len(extrafields)==0):
            self.set_extrafields_dict(None)
        else:
            self.set_extrafields_dict(extrafields)







    @classmethod
    def define_fields(cls, dbmanager):
        """This class-level function defines the database fields for this model -- the columns, etc."""
        fieldlist = [
            # standard primary id number field
            mdbfield.DbfPrimaryId('id', {
                'label': "The primary key and id# for this row"
                }),
            # an arbitrarily long string serializing any other log properties that we don't have explicit fields for.
            mdbfield.DbfSerialized('extrafields_serialized', {
                'label': "Arbitrary dictionary of extra fields"
                }),
            # actual log msg text
            mdbfield.DbfTimestamp('timestamp', {
                'label': "The timestamp for the message"
                }),
            # actual log msg text
            mdbfield.DbfText('msg', {
                'label': "The text message"
                }),
            # actual log msg text
            mdbfield.DbfString('source', {
                'label': "The source of the message"
                }),
            # actual log msg text
            mdbfield.DbfString('type', {
                'label': "The type of the message"
                }),
            # globally unique subject reference (usually the user logged in)
            mdbmixins.dbfmixin_gobreference('subject'),
            # globally unique resource reference (could be a document, group, thread, etc.)
            mdbmixins.dbfmixin_gobreference('resource'),
            ]

        return fieldlist
