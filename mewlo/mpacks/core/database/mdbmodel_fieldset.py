"""
mdbmodelfieldset.py
MewloDbFieldset is a helper MewloDbObject that holds a set of fields in a has-a relationship with another object.
You can how this class is used via calls to make_fieldset_dbobjectclass() from muser.py and mgroup.py,
 essentially they allow the dynamic creation of helper database tables that are associated with users and groups, etc.
"""


# mewlo imports
from ..helpers import misc
import mdbmodel
import mdbfield




class MewloDbFieldset(mdbmodel.MewloDbModel):
    """Helper MewloDbObject that holds a set of fields in a has-a relationship with another object."""

    @classmethod
    def set_ownerclass(cls, ownerclass):
        cls.ownerclass = ownerclass

    @classmethod
    def define_fields(cls, dbmanager):
        """This class-level function defines the database fields for this model."""

        ownerfieldid = cls.ownerclass.get_dbtablename()+'_id'
        fieldlist = [
            # standard primary id number field
            mdbfield.DbfPrimaryId('id', {
                'label': "The primary key and id# for this row"
                }),
            # and now we are going to add a 1-to-1 field from us back to the object we are properties foe
            mdbfield.Dbf1to1_Right(ownerfieldid, {
                'label': 'Reference to owner object',
                'leftclass': cls.ownerclass,
                }),
            ]

        return fieldlist








    @classmethod
    def make_fieldset_dbobjectclass(cls, ownerclass, propname, proplabel, backrefname, dbmanager, subfields):
        """Make a new derived database model class that will store some fields in a has-a relationship with us."""

        # ok dynamically create a new class for this purpose -- note the base class IS derived from MewloDbFieldset above (cls)
        basesubclass = cls
        subclassname = ownerclass.__name__ + '_' + propname
        subclasstablename = ownerclass.get_dbtablename()+'_'+propname
        # NOTE: we call create_derived_dbmodelclass() to dynamically on the fly create a new model class based on an existing one, but with unique table, etc.
        subclass = dbmanager.create_derived_dbmodelclass(ownerclass, basesubclass, subclassname, subclasstablename)

        # set owner of this new subclass
        subclass.set_ownerclass(ownerclass)

        # now add the fields we were asked to add to it
        subclass.extend_fields(subfields)

        # and now register the new subclass with the manager
        dbmanager.register_modelclass(ownerclass, subclass)

        # now add field refering to this subclass to the owner class
        fieldlist = [
            mdbfield.Dbf1to1_Left(propname, {
            'label': proplabel,
            'rightclass': subclass,
            'backrefname': backrefname,
            }),
            ]

        # add to the owner class a field pointing to this new helper class
        ownerclass.extend_fields(fieldlist)






