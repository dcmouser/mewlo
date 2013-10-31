"""
mdbmodel.py

This is our database object base class.

"""


# mewlo imports
from ..helpers import misc
import mdbfield

# python imports
import pickle






class MewloDbModel(object):
    """An object that represents a database model."""

    # class variables
    dbtablename = None
    dbschemaname = None
    #
    dbsqlatable = None
    dbsqlahelper = None
    dbmanager = None
    #
    fieldlist = []
    fielddict = {}
    #
    propertysets = {}


    # ATTN: NOTE __INIT__ IS *NOT* CALLED WHEN INSTANTIATING MODELS VIA SQLALCHEMY ORM SO WE AVOID IT WHERE POSSIBLE


















    # These methods should not have to be re-implemented by dervived subclasses

    def add(self):
        """Add the model to database."""
        self.dbm().model_add(self)

    def save(self):
        """Update/Save the model to database."""
        self.add()

    def delete(self):
        """Delete the model from database."""
        self.dbm().model_delete(self)





    @classmethod
    def dbm(cls):
        """Shortcut to get info from class object."""
        return cls.dbmanager

    @classmethod
    def dbsession(cls):
        """Shortcut to get info from class object."""
        sqlahelper = cls.dbsqlahelper
        return sqlahelper.getmake_session()

    @classmethod
    def get_dbtablename(cls):
        return cls.dbtablename

    @classmethod
    def get_dbschemaname(cls):
        return cls.dbschemaname

    @classmethod
    def setclass_dbinfo(cls, sqlatable, sqlahelper, dbmanager):
        """Store data in class regarding datbase access for it."""
        # ATTN: TODO - some of this may not be needed, this may be automatically added to the class itself by sqlalchemy
        cls.dbsqlatable = sqlatable
        cls.dbsqlahelper = sqlahelper
        cls.dbmanager = dbmanager

    @classmethod
    def set_dbnames(cls, tablename, schemaname):
        cls.dbtablename = tablename
        cls.dbschemaname = schemaname

    @classmethod
    def get_fieldlist(cls):
        """Return the database fields."""
        return cls.fieldlist

    @classmethod
    def get_fielddict(cls):
        """Return the database fields."""
        return cls.fielddict

    @classmethod
    def register_fieldlist(cls, fieldlist):
        """save fields."""
        cls.fieldlist = fieldlist
        for field in fieldlist:
            cls.fielddict[field.id] = field




    @classmethod
    def delete_all(cls):
        """Delete all items (rows) in the table."""
        cls.dbm().modelclass_deleteall(cls)

    @classmethod
    def delete_bykey(cls, keydict):
        """Delete all items (rows) matching key dictionary settings."""
        cls.dbm().modelclass_deletebykey(cls, keydict)

    @classmethod
    def find_one_bykey(cls, keydict, defaultval):
        """Find and return an instance object for the single row specified by keydict.
        :return: defaultval if not found
        """
        return cls.dbm().modelclass_find_one_bykey(cls, keydict, defaultval)

    @classmethod
    def find_all(cls):
        """Load *all* rows and return them as array."""
        return cls.dbm().modelclass_find_all(cls)

    @classmethod
    def serialize(cls, obj):
        """Helper function to serialize arbitrary object."""
        return misc.serialize_for_readability(obj)

    @classmethod
    def unserialize(cls, serializedtext):
        """Helper function to unserialize arbitrary text."""
        return pickle.loads(str(serializedtext))

    @classmethod
    def new(cls):
        """Make a new instance of the class."""
        return cls()





















    # These methods will be specific to the derived subclass

    @classmethod
    def definedb(cls, dbmanager):
        """This class-level function defines the database fields for this model -- the columns, etc.
        The subclass will implement this function."""
        pass



    @classmethod
    def create_subclasses(cls, dbmanager):
        """
        Give this model class the opportunity to recursively call manager to register/map (via map_modelclass() function), subclasses used privately by this class.
        This is useful especially when we have PropertySet tables for an object.
        """
        pass









    @classmethod
    def make_fieldset_dbobjectclass(cls, propname, proplabel, dbmanager, subfields):
        """Make a new database model class that will store some fields in a has-a relationship with us."""

        # init
        fieldlist = []

        # ok dynamically create a new class for this purpose
        subclassname = cls.__name__ + '_' + propname
        subclasstablename = cls.get_dbtablename()+'_'+propname
        basesubclass = MewloDbFieldset
        subclass = dbmanager.create_derived_dbmodelclass(cls, basesubclass, subclassname, subclasstablename)

        # set owner of this subclass
        subclass.set_owner(cls)
        # now provide the subclass with the subfields
        subclass.add_subfields(subfields)

        # now add field refering to this subclass from the owner class
        fieldlist += [
            mdbfield.Dbf1to1_Left(propname, {
            'label': proplabel,
            'referenceclass': subclass,
            }),
            ]

        # and now register the subclass with the manager
        dbmanager.register_modelclass(cls, subclass)

        return fieldlist
















class MewloDbFieldset(MewloDbModel):
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
        #fieldname = cls.__name__ + '_id'
        fieldname = 'owner_id'
        fieldlist += [
            mdbfield.Dbf1to1_Right(fieldname, {
            'label': 'Reference to owner object',
            'referenceclass': cls.ownerclass,
            }),
            ]

        cls.register_fieldlist(fieldlist)
