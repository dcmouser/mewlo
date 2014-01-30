"""
mdbfield.py
The MewloDbField class handles one column of a model.

The approach we take is that each model in the system (MewloDbModel in mdbmodel.py) defined a list of MewloDbFields.
The MewloDbFields roughly map to columns in a database table, but may also define relationships with other tables (absent a column).
The MewloDbField should define all information needed for not just database storage but also visual display, sorting, searching, etc.
That is, we are aiming for a DRY approach to model data by storing information in MewloDbFields.
They also serve as a layer of abstraction on top of the SqlAlchemy library, which does the heavy lifting.

ATTN: THIS CODE NEEDS REVIEW/REWRITING -- especially the relations code
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
        self.sqlacolumns = []


    def set_sqlacolumns(self, sqlacolumns):
        self.sqlacolumns = sqlacolumns
    def get_sqlacolumns(self):
        return self.sqlacolumns
    def get_sqlacolumn(self):
        return self.sqlacolumns[0]


    def create_sqlalchemy_columns(self, modelclass):
        """Convert field to sqlalchemy column."""
        # subclass may override this
        return None

    def create_sqlalchemy_mapperproperties(self, modelclass, modeltable):
        """Convert field to sqlalchemy column."""
        # subclass may override this
        return None




















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
        return [sqlalchemy.Column(self.id, sqlalchemy.String(get_value_from_dict(self.properties,'length',256)))]




class DbfUsername(MewloDbField):
    """Limited length text field."""
    def __init__(self, id, properties={}):
        """Constructor."""
        # call parent function
        super(DbfUsername, self).__init__(id, properties)
    def create_sqlalchemy_columns(self, modelclass):
        """Convert field to sqlalchemy column."""
        return [sqlalchemy.Column(self.id, sqlalchemy.String(get_value_from_dict(self.properties,'length',32)))]

class DbfEmail(MewloDbField):
    """Limited length text field."""
    def __init__(self, id, properties={}):
        """Constructor."""
        # call parent function
        super(DbfEmail, self).__init__(id, properties)
    def create_sqlalchemy_columns(self, modelclass):
        """Convert field to sqlalchemy column."""
        return [sqlalchemy.Column(self.id, sqlalchemy.String(get_value_from_dict(self.properties,'length',96)))]

class DbfHashedPassword(MewloDbField):
    """Limited length text field."""
    def __init__(self, id, properties={}):
        """Constructor."""
        # call parent function
        super(DbfHashedPassword, self).__init__(id, properties)
    def create_sqlalchemy_columns(self, modelclass):
        """Convert field to sqlalchemy column."""
        return [sqlalchemy.Column(self.id, sqlalchemy.String(get_value_from_dict(self.properties,'length',256)))]






class DbfInteger(MewloDbField):
    """Integer field."""
    def __init__(self, id, properties={}):
        """Constructor."""
        # call parent function
        super(DbfInteger, self).__init__(id, properties)

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







class DbfTypeString(MewloDbField):
    """Limited length text field."""
    # ATTN: unfinished
    def __init__(self, id, properties={}):
        """Constructor."""
        # call parent function
        super(DbfTypeString, self).__init__(id, properties)

    def create_sqlalchemy_columns(self, modelclass):
        """Convert field to sqlalchemy column."""
        return [sqlalchemy.Column(self.id, sqlalchemy.String(get_value_from_dict(self.properties,'length',64)))]


class DbfVarname(MewloDbField):
    """Limited length text field."""
    def __init__(self, id, properties={}):
        """Constructor."""
        # call parent function
        super(DbfVarname, self).__init__(id, properties)
    def create_sqlalchemy_columns(self, modelclass):
        """Convert field to sqlalchemy column."""
        return [sqlalchemy.Column(self.id, sqlalchemy.String(get_value_from_dict(self.properties,'length',32)))]



class DbfSerialized(MewloDbField):
    """Unlimited length text field used to serialize/unserialized arbitrary primitive types (dictionaries, etc.)"""
    # ATTN: unfinished
    def __init__(self, id, properties={}):
        """Constructor."""
        # call parent function
        super(DbfSerialized, self).__init__(id, properties)

    def create_sqlalchemy_columns(self, modelclass):
        """Convert field to sqlalchemy column."""
        return [sqlalchemy.Column(self.id, sqlalchemy.Text())]



class DbfEnum(MewloDbField):
    """Enumerated field."""
    # ATTN: unfinished
    def __init__(self, id, properties={}):
        """Constructor."""
        # call parent function
        super(DbfEnum, self).__init__(id, properties)

    def create_sqlalchemy_columns(self, modelclass):
        """Convert field to sqlalchemy column."""
        return [sqlalchemy.Column(self.id, sqlalchemy.Integer)]





class DbfForeignKey(MewloDbField):
    """Foreign Key."""
    # ATTN: Make this a foreign key to user table
    def __init__(self, id, properties={}):
        """Constructor."""
        # call parent function
        super(DbfForeignKey, self).__init__(id, properties)

    def create_sqlalchemy_columns(self, modelclass):
        """Convert field to sqlalchemy column."""
        foreignkeyname = self.properties['foreignkeyname']
        return [sqlalchemy.Column(self.id, None, sqlalchemy.ForeignKey(foreignkeyname))]


class DbfForeignKeyFromClassId(DbfForeignKey):
    """Foreign Key to a class id."""
    # ATTN: Make this a foreign key to user table
    def __init__(self, id, properties={}):
        """Constructor."""
        # call parent function
        super(DbfForeignKeyFromClassId, self).__init__(id, properties)
        referenceclass = self.properties['referenceclass']
        self.properties['foreignkeyname'] = referenceclass.get_dbtablename() + '.id'



class DbfForeignUserId(DbfForeignKeyFromClassId):
    """Foreign Key to User class id."""
    def __init__(self, id, properties={}):
        """Constructor."""
        from ..user import muser
        properties['referenceclass'] = muser.MewloUser
        super(DbfForeignUserId, self).__init__(id, properties)












class DbfForeignPrimaryKey(MewloDbField):
    """Integer field."""
    # ATTN: Make this a foreign key to user table
    def __init__(self, id, properties={}):
        """Constructor."""
        # call parent function
        super(DbfForeignPrimaryKey, self).__init__(id, properties)

    def create_sqlalchemy_columns(self, modelclass):
        """Convert field to sqlalchemy column."""
        foreignkeyname = self.properties['foreignkeyname']
        return [sqlalchemy.Column(self.id, None, sqlalchemy.ForeignKey(foreignkeyname),primary_key=True)]





class DbfServerIp(MewloDbField):
    """Ip of an accessing computer."""
    def __init__(self, id, properties={}):
        """Constructor."""
        # call parent function
        super(DbfServerIp, self).__init__(id, properties)

    def create_sqlalchemy_columns(self, modelclass):
        """Convert field to sqlalchemy column."""
        return [sqlalchemy.Column(self.id, sqlalchemy.String(get_value_from_dict(self.properties,'length',32)))]





class DbfCryptoHash(MewloDbField):
    """Ip of an accessing computer."""
    def __init__(self, id, properties={}):
        """Constructor."""
        # call parent function
        super(DbfCryptoHash, self).__init__(id, properties)

    def create_sqlalchemy_columns(self, modelclass):
        """Convert field to sqlalchemy column."""
        return [sqlalchemy.Column(self.id, sqlalchemy.String(get_value_from_dict(self.properties,'length',64)))]







class DbfSqla(MewloDbField):
    """A dbf field that is passed a prebuilt sql alchemy column."""
    def __init__(self, id, properties, sqlacolumns):
        """Constructor."""
        # call parent function
        super(DbfPrimaryId, self).__init__(id, properties)
        # record passed in sqlacolumns
        self.set_sqlacolumns(sqlacolumns)

    def create_sqlalchemy_columns(self, modelclass):
        """Convert field to sqlalchemy column."""
        return self.sqlacolumns


















































# These relational fields are ugly and need fixing.






class Dbf1toN_Left(MewloDbField):
    """Relationship field."""
    def __init__(self, id, properties={}, flag_to1=False):
        """Constructor."""
        # call parent function
        super(Dbf1toN_Left, self).__init__(id, properties)
        self.flag_to1 = flag_to1

    def create_sqlalchemy_mapperproperties(self, modelclass, modeltable):
        """Convert field to sqlalchemy column."""
        # we dont use a column but a relation
        rightclass = self.properties['rightclass']
        rightclass_relationname = self.id
        backrefname = self.properties['backrefname']
        # now we need to look up the owner_id field on the right hand side so we can explicitly specify it as the foreign_key for this relations
        # this is important because the sqla relation will error and complain about ambiguity if there are multiple columns with foreign keys to us on the right hand (reference class) side
        fkeyfieldname = modelclass.get_dbtablename()+'_id'
        foreign_keys = rightclass.lookup_sqlacolumnlist_for_field(fkeyfieldname)
        # create the relation
        propdict = {
            rightclass_relationname:sqlalchemy.orm.relation(rightclass, uselist=not self.flag_to1, backref=backrefname, foreign_keys=foreign_keys)
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
        leftclass = self.properties['leftclass']
        fkeyfieldname = 'id'
        fkeyname = leftclass.get_dbtablename() + '.' + fkeyfieldname
        return [sqlalchemy.Column(self.id, None, sqlalchemy.ForeignKey(fkeyname))]






class Dbf1to1_Left(Dbf1toN_Left):
    """Relationship field."""
    def __init__(self, id, properties={}):
        """Constructor."""
        # call parent function to do the work
        super(Dbf1to1_Left, self).__init__(id, properties, flag_to1=True)


class Dbf1to1_Right(Dbf1toN_Right):
    """Relationship field."""
    def __init__(self, id, properties={}):
        """Constructor."""
        # call parent function to do the work
        super(Dbf1to1_Right, self).__init__(id, properties, flag_to1=True)









class Dbf1to1_OneWay(MewloDbField):
    """Relationship field."""
    def __init__(self, id, properties={}):
        """Constructor."""
        # call parent function
        super(Dbf1to1_OneWay, self).__init__(id, properties)


    def create_sqlalchemy_columns(self, modelclass):
        """Convert field to sqlalchemy column."""
        # build a foreign key to the right hand table
        rightclass = self.properties['rightclass']
        fkeyfieldname = 'id'
        fkeyname = rightclass.get_dbtablename() + '.' + fkeyfieldname
        return [sqlalchemy.Column(self.id, None, sqlalchemy.ForeignKey(fkeyname))]

    def create_sqlalchemy_mapperproperties(self, modelclass, modeltable):
        """Convert field to sqlalchemy column."""
        # simple one-way relation, no backref
        rightclass = self.properties['rightclass']
        rightclass_relationname = self.properties['relationname']
        #
        foreign_keys=[self.get_sqlacolumn()]

        # create the relation
        propdict = {
            rightclass_relationname:sqlalchemy.orm.relation(rightclass, uselist=False, foreign_keys = foreign_keys)
            }
        return propdict










class DbfNtoM_SimpleRelation(MewloDbField):
    """Relationship field."""
    def __init__(self, id, properties={}):
        """Constructor."""
        # call parent function
        super(DbfNtoM_SimpleRelation, self).__init__(id, properties)

    def create_sqlalchemy_mapperproperties(self, modelclass, modeltable):
        """Convert field to sqlalchemy column."""
        # we dont use a column but a relation
        associationclass = self.properties['associationclass']
        otherclass = self.properties['otherclass']
        if ('backrefname' in self.properties):
            backref = self.properties['backrefname']
        else:
            backref = None
        relationname = self.id
        if (associationclass!=None):
            associationtable = associationclass.get_dbsqlatable()
        else:
            associationtable = None

        if ('foreign_keyname' in self.properties):
            foreign_keys = associationclass.lookup_sqlacolumnlist_for_field(self.properties['foreign_keyname'])
        else:
            foreign_keys = None

        if ('backref_foreign_keyname' in self.properties):
            backref_foreign_keys = associationclass.lookup_sqlacolumnlist_for_field(self.properties['backref_foreign_keyname'])
            fullbackref = sqlalchemy.orm.backref(backref,foreign_keys=backref_foreign_keys)
            backref = fullbackref
            #print "BACKREFFOREIGN "+self.properties['backref_foreign_keyname'] + str(backref_foreign_keys)
        else:
            backref_foreign_keys = None

        #print "Creating relation on {0} named {1} otherclass = {2} and secondary={3} and backref={4}.".format(modelclass.__name__,relationname, otherclass.__name__, associationtable, backrefname)

        # create the relation
        propdict = {
            relationname:sqlalchemy.orm.relation(otherclass, secondary=associationtable, backref=backref, foreign_keys=foreign_keys)
            }
        return propdict










class Dbf_SelfSelfRelation(MewloDbField):
    """Relationship field."""
    def __init__(self, id, properties={}):
        """Constructor."""
        # call parent function
        super(Dbf_SelfSelfRelation, self).__init__(id, properties)

    def create_sqlalchemy_mapperproperties(self, modelclass, modeltable):
        """Convert field to sqlalchemy column."""
        # we dont use a column but a relation
        associationclass = self.properties['associationclass']
        otherclass = self.properties['otherclass']
        backref = self.properties['backrefname']
        relationname = self.id
        associationtable = associationclass.get_dbsqlatable()

        # ok now we need to specify primaryjoin and secondary join
        # this turns out to be incredibly f*cked up because sqlalchemy is trying to be so clever and magic with they way it lets you use overloaded operators to specify parameters
        # and because it inexplicably does not allow us to pass string expressions when using classic definition
        # get names of join variables (parent and child)
        primaryjoin_name = self.properties['primaryjoin_name']
        secondaryjoin_name = self.properties['secondaryjoin_name']
        # look up sqlalchemy COLUMNS
        otheridcolumn = otherclass.lookup_sqlacolumn_for_field('id')
        primaryjoin_column = associationclass.lookup_sqlacolumn_for_field(primaryjoin_name)
        secondaryjoin_column = associationclass.lookup_sqlacolumn_for_field(secondaryjoin_name)
        # and now the actual join parameters are these f*cked magic expressions (once again being clever and magic creates evilness)
        # stupid, annoying, painful
        primaryjoin = otheridcolumn == primaryjoin_column
        secondaryjoin = otheridcolumn == secondaryjoin_column
        # create the relation
        propdict = {
            relationname:sqlalchemy.orm.relation(otherclass, secondary=associationtable, backref=backref, primaryjoin=primaryjoin, secondaryjoin=secondaryjoin)
            }
        return propdict





