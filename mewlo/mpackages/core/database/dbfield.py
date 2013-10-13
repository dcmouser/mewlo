"""
dbfield.py

The DbField class handles one column of a model.

"""


# helper imports

# python imports

# library imports
import sqlalchemy






class DbField(object):
    """The DbField object represents a column in a database and contains ancillary information for gui stuff."""

    def __init__(self, id, properties):
        """Constructor."""
        # init
        self.id = id
        self.properties = properties







class DbfPrimaryId(DbField):
    """Standard numeric autoinc unique primary id field."""
    def __init__(self, id='id', properties={}):
        """Constructor."""
        # call parent function
        super(DbfPrimaryId, self).__init__(id, properties)

    def convert_to_sqlalchemy_column(self):
        """Convert field to sqlalchemy column."""
        return sqlalchemy.Column(self.id, sqlalchemy.Integer, primary_key=True)




class DbfUniqueKeyname(DbField):
    """Short unique indexed key."""
    def __init__(self, id, properties={}):
        """Constructor."""
        # call parent function
        super(DbfUniqueKeyname, self).__init__(id, properties)

    def convert_to_sqlalchemy_column(self):
        """Convert field to sqlalchemy column."""
        return sqlalchemy.Column(self.id, sqlalchemy.String(64), unique = True)




class DbfSerialized(DbField):
    """Unlimited length text field used to serialize/unserialized arbitrary primitive types (dictionaries, etc.)"""
    def __init__(self, id, properties={}):
        """Constructor."""
        # call parent function
        super(DbfSerialized, self).__init__(id, properties)


    def convert_to_sqlalchemy_column(self):
        """Convert field to sqlalchemy column."""
        return sqlalchemy.Column(self.id, sqlalchemy.Text())

