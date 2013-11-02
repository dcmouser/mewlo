"""
mdbmodelfieldset.py

Fieldset helpers

"""


# mewlo imports
from ..helpers import misc
import mdbmodel
import mdbfield







class MewloDbFieldset(mdbmodel.MewloDbModel):
    """Helper MewloDbObject that holds a set of fields in a has-a relationship with another object."""

    # class variables
    subfields = []

    @classmethod
    def set_owner(cls, ownerclass):
        cls.ownerclass = ownerclass

    @classmethod
    def add_subfields(cls, subfields):
        cls.subfields += subfields


    @classmethod
    def definedb(cls, dbmanager):
        """This class-level function defines the database fields for this model."""

        # starting field list is just primary id
        fieldlist = [
            # standard primary id number field
            mdbfield.DbfPrimaryId('id', {
                'label': "The primary key and id# for this row"
                }),
            ]

        # add subfields we were asked to add
        fieldlist += cls.subfields

        # and now we are going to add a 1-to-1 field from us back to the object we are properties foe
        fieldlist += [
            mdbfield.Dbf1to1_Right('owner_id', {
            'label': 'Reference to owner object',
            'referenceclass': cls.ownerclass,
            }),
            ]

        cls.hash_fieldlist(fieldlist)









    @classmethod
    def make_fieldset_dbobjectclass(cls, ownerclass, propname, proplabel, backrefname, dbmanager, subfields):
        """Make a new database model class that will store some fields in a has-a relationship with us."""

        # init
        basesubclass = cls
        fieldlist = []

        # ok dynamically create a new class for this purpose
        subclassname = ownerclass.__name__ + '_' + propname
        subclasstablename = ownerclass.get_dbtablename()+'_'+propname
        # NOTE: we call create_derived_dbmodelclass() to dynamically on the fly create a new model class based on an existing one, but with unique table, etc.
        subclass = dbmanager.create_derived_dbmodelclass(ownerclass, basesubclass, subclassname, subclasstablename)

        # set owner of this subclass
        subclass.set_owner(ownerclass)
        # now provide the subclass with the subfields
        subclass.add_subfields(subfields)
        # foreign key name
        foreignkeyname = subclass.__name__ + ".id"

        # and now register the subclass with the manager
        dbmanager.register_modelclass(ownerclass, subclass)

        # now add field refering to this subclass from the owner class
        fieldlist += [
            mdbfield.Dbf1to1_Left(propname, {
            'label': proplabel,
            'referenceclass': subclass,
            'backrefname': backrefname,
            'foreignkeyname': foreignkeyname,
            }),
            ]

        return fieldlist





