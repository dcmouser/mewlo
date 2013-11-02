"""
mdbfield.py

The MewloDbField class handles one column of a model.

"""


# mewlo imports
from ..helpers.misc import get_value_from_dict


# python imports

# library imports
import sqlalchemy






class MewloDbField(object):
    """The DbField object represents a column in a database and contains ancillary information for gui stuff."""

    def __init__(self, id, properties):
        """Constructor."""
        # init
        self.id = id
        self.properties = properties

    def create_sqlalchemy_columns(self, modelclass):
        """Convert field to sqlalchemy column."""
        return None
    def create_sqlalchemy_mapperproperties(self, modelclass):
        """Convert field to sqlalchemy column."""
        return None

    def set_sqlacolumns(self, columns):
        """Record sqlacolumns for future use."""
        self.sqlacolumns = columns






class DbfPrimaryId(MewloDbField):
    """Standard numeric autoinc unique primary id field."""
    def __init__(self, id='id', properties={}):
        """Constructor."""
        # call parent function
        super(DbfPrimaryId, self).__init__(id, properties)

    def create_sqlalchemy_columns(self, modelclass):
        """Convert field to sqlalchemy column."""
        return [sqlalchemy.Column(self.id, sqlalchemy.Integer, primary_key=True)]




class DbfUniqueKeyname(MewloDbField):
    """Short unique indexed key."""
    def __init__(self, id, properties={}):
        """Constructor."""
        # call parent function
        super(DbfUniqueKeyname, self).__init__(id, properties)

    def create_sqlalchemy_columns(self, modelclass):
        """Convert field to sqlalchemy column."""
        return [sqlalchemy.Column(self.id, sqlalchemy.String(64), unique = True)]




class DbfSerialized(MewloDbField):
    """Unlimited length text field used to serialize/unserialized arbitrary primitive types (dictionaries, etc.)"""
    def __init__(self, id, properties={}):
        """Constructor."""
        # call parent function
        super(DbfSerialized, self).__init__(id, properties)

    def create_sqlalchemy_columns(self, modelclass):
        """Convert field to sqlalchemy column."""
        return [sqlalchemy.Column(self.id, sqlalchemy.Text())]




class DbfText(MewloDbField):
    """Unlimited length text field."""
    def __init__(self, id, properties={}):
        """Constructor."""
        # call parent function
        super(DbfText, self).__init__(id, properties)

    def create_sqlalchemy_columns(self, modelclass):
        """Convert field to sqlalchemy column."""
        return [sqlalchemy.Column(self.id, sqlalchemy.Text())]



class DbfString(MewloDbField):
    """Limited length text field."""
    def __init__(self, id, properties={}):
        """Constructor."""
        # call parent function
        super(DbfString, self).__init__(id, properties)

    def create_sqlalchemy_columns(self, modelclass):
        """Convert field to sqlalchemy column."""
        return [sqlalchemy.Column(self.id, sqlalchemy.String(get_value_from_dict(self.properties,'length',64)))]



class DbfInteger(MewloDbField):
    """Integer field."""
    def __init__(self, id, properties={}):
        """Constructor."""
        # call parent function
        super(DbfInteger, self).__init__(id, properties)

    def create_sqlalchemy_columns(self, modelclass):
        """Convert field to sqlalchemy column."""
        return [sqlalchemy.Column(self.id, sqlalchemy.Integer)]



class DbfEnum(MewloDbField):
    """Integer field."""
    def __init__(self, id, properties={}):
        """Constructor."""
        # call parent function
        super(DbfEnum, self).__init__(id, properties)

    def create_sqlalchemy_columns(self, modelclass):
        """Convert field to sqlalchemy column."""
        return [sqlalchemy.Column(self.id, sqlalchemy.Integer)]



class DbfBigInteger(MewloDbField):
    """BigInteger field."""
    def __init__(self, id, properties={}):
        """Constructor."""
        # call parent function
        super(DbfBigInteger, self).__init__(id, properties)

    def create_sqlalchemy_columns(self, modelclass):
        """Convert field to sqlalchemy column."""
        return [sqlalchemy.Column(self.id, sqlalchemy.BigInteger)]


class DbfFloat(MewloDbField):
    """Float field."""
    def __init__(self, id, properties={}):
        """Constructor."""
        # call parent function
        super(DbfFloat, self).__init__(id, properties)

    def create_sqlalchemy_columns(self, modelclass):
        """Convert field to sqlalchemy column."""
        return [sqlalchemy.Column(self.id, sqlalchemy.Float)]

class DbfTimestamp(MewloDbField):
    """Timestamp field."""
    def __init__(self, id, properties={}):
        """Constructor."""
        # call parent function
        super(DbfTimestamp, self).__init__(id, properties)

    def create_sqlalchemy_columns(self, modelclass):
        """Convert field to sqlalchemy column."""
        return [sqlalchemy.Column(self.id, sqlalchemy.Float)]





class DbfBoolean(MewloDbField):
    """Integer field."""
    def __init__(self, id, properties={}):
        """Constructor."""
        # call parent function
        super(DbfBoolean, self).__init__(id, properties)

    def create_sqlalchemy_columns(self, modelclass):
        """Convert field to sqlalchemy column."""
        return [sqlalchemy.Column(self.id, sqlalchemy.Boolean)]




class DbfForeignUserId(MewloDbField):
    """Integer field."""
    # ATTN: Make this a foreign key to user table
    def __init__(self, id, properties={}):
        """Constructor."""
        # call parent function
        super(DbfForeignUserId, self).__init__(id, properties)

    def create_sqlalchemy_columns(self, modelclass):
        """Convert field to sqlalchemy column."""
        from ..user import muser
        referenceclass = muser.MewloUser
        fkeyfieldname = 'id'
        fkeyname = referenceclass.get_dbtablename() + '.' + fkeyfieldname
        return [sqlalchemy.Column(self.id, None, sqlalchemy.ForeignKey(fkeyname))]



class DbfUserIp(MewloDbField):
    """Limited length text field."""
    def __init__(self, id, properties={}):
        """Constructor."""
        # call parent function
        super(DbfUserIp, self).__init__(id, properties)

    def create_sqlalchemy_columns(self, modelclass):
        """Convert field to sqlalchemy column."""
        return [sqlalchemy.Column(self.id, sqlalchemy.String(get_value_from_dict(self.properties,'length',32)))]














class Dbf1toN_Left(MewloDbField):
    """Relationship field."""
    def __init__(self, id, properties={}, flag_to1=False):
        """Constructor."""
        # call parent function
        super(Dbf1toN_Left, self).__init__(id, properties)
        self.flag_to1 = flag_to1

    def create_sqlalchemy_mapperproperties(self, modelclass):
        """Convert field to sqlalchemy column."""
        # we dont use a column but a relation
        referenceclass = self.properties['referenceclass']
        referencefieldname = self.id
        backrefname = self.properties['backrefname']
        # now we need to look up the owner_id field on the right hand side so we can explicitly specify it as the foreign_key for this relations
        # this is important because the sqla relation will error and complain about ambiguity if there are multiple columns with foreign keys to us on the right hand (reference class) side
        foreign_keys = referenceclass.lookup_sqlacolumnlist_for_field('owner_id')
        # create the relation
        propdict = {
            referencefieldname:sqlalchemy.orm.relation(referenceclass, uselist=not self.flag_to1, backref=backrefname, foreign_keys=foreign_keys)
            }
        return propdict


class Dbf1toN_Right(MewloDbField):
    """Relationship field."""
    def __init__(self, id, properties={}, flag_to1=False):
        """Constructor."""
        # call parent function
        super(Dbf1toN_Right, self).__init__(id, properties)
        self.flag_to1 = flag_to1

    def create_sqlalchemy_columns(self, modelclass):
        """Convert field to sqlalchemy column."""
        # build a foreign key to the left hand table
        referenceclass = self.properties['referenceclass']
        fkeyfieldname = 'id'
        fkeyname = referenceclass.get_dbtablename() + '.' + fkeyfieldname
        return [sqlalchemy.Column(self.id, None, sqlalchemy.ForeignKey(fkeyname))]






class Dbf1to1_Left(Dbf1toN_Left):
    """Relationship field."""
    def __init__(self, id, properties={}):
        """Constructor."""
        # call parent function
        super(Dbf1to1_Left, self).__init__(id, properties, flag_to1=True)


class Dbf1to1_Right(Dbf1toN_Right):
    """Relationship field."""
    def __init__(self, id, properties={}):
        """Constructor."""
        # call parent function
        super(Dbf1to1_Right, self).__init__(id, properties, flag_to1=True)











class DbfSqla(MewloDbField):
    """A dbf field that is passed a prebuilt sql alchemy column."""
    def __init__(self, id, properties, sqlacolumns):
        """Constructor."""
        # call parent function
        super(DbfPrimaryId, self).__init__(id, properties)
        # record passed in sqlacolumns
        self.sqlacolumns = sqlacolumns

    def create_sqlalchemy_columns(self, modelclass):
        """Convert field to sqlalchemy column."""
        return self.sqlacolumns