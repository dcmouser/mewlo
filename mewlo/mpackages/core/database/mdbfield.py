"""
mdbfield.py

The MewloDbField class handles one column of a model.

"""


# helper imports
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







class DbfPrimaryId(MewloDbField):
    """Standard numeric autoinc unique primary id field."""
    def __init__(self, id='id', properties={}):
        """Constructor."""
        # call parent function
        super(DbfPrimaryId, self).__init__(id, properties)

    def convert_to_sqlalchemy_column(self):
        """Convert field to sqlalchemy column."""
        return sqlalchemy.Column(self.id, sqlalchemy.Integer, primary_key=True)




class DbfUniqueKeyname(MewloDbField):
    """Short unique indexed key."""
    def __init__(self, id, properties={}):
        """Constructor."""
        # call parent function
        super(DbfUniqueKeyname, self).__init__(id, properties)

    def convert_to_sqlalchemy_column(self):
        """Convert field to sqlalchemy column."""
        return sqlalchemy.Column(self.id, sqlalchemy.String(64), unique = True)




class DbfSerialized(MewloDbField):
    """Unlimited length text field used to serialize/unserialized arbitrary primitive types (dictionaries, etc.)"""
    def __init__(self, id, properties={}):
        """Constructor."""
        # call parent function
        super(DbfSerialized, self).__init__(id, properties)

    def convert_to_sqlalchemy_column(self):
        """Convert field to sqlalchemy column."""
        return sqlalchemy.Column(self.id, sqlalchemy.Text())




class DbfText(MewloDbField):
    """Unlimited length text field."""
    def __init__(self, id, properties={}):
        """Constructor."""
        # call parent function
        super(DbfText, self).__init__(id, properties)

    def convert_to_sqlalchemy_column(self):
        """Convert field to sqlalchemy column."""
        return sqlalchemy.Column(self.id, sqlalchemy.Text())



class DbfString(MewloDbField):
    """Unlimited length text field."""
    def __init__(self, id, properties={}):
        """Constructor."""
        # call parent function
        super(DbfString, self).__init__(id, properties)

    def convert_to_sqlalchemy_column(self):
        """Convert field to sqlalchemy column."""
        return sqlalchemy.Column(self.id, sqlalchemy.String(get_value_from_dict(self.properties,'length',64)))






class DbfSqla(MewloDbField):
    """A dbf field that is passed a prebuilt sql alchemy column."""
    def __init__(self, id, properties, sqlacolumn):
        """Constructor."""
        # call parent function
        super(DbfPrimaryId, self).__init__(id, properties)
        # record passed in sqlacolumn
        self.sqlacolumn = sqlacolumn

    def convert_to_sqlalchemy_column(self):
        """Convert field to sqlalchemy column."""
        return self.sqlacolumn
