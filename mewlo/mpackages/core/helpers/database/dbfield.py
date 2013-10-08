"""
dbfield.py

The DbField class handles one column of a model.

"""


# helper imports

# python imports







class DbField(object):
    """The DbField object represents a column in a database and contains ancillary information for gui stuff."""

    def __init__(self, name, properties):
        """Constructor."""
        # init
        self.name = name
        self.properties = properties







class DbfPrimaryId(DbField):
    """Standard numeric autoinc unique primary id field."""
    def __init__(self, name, properties={}):
        """Constructor."""
        # call parent function
        super(DbfPrimaryId, self).__init__(name, properties)



class DbfUniqueKeyname(DbField):
    """Short unique indexed key."""
    def __init__(self, name, properties={}):
        """Constructor."""
        # call parent function
        super(DbfUniqueKeyname, self).__init__(name, properties)


class DbfSerialized(DbField):
    """Unlimited length text field used to serialize/unserialized arbitrary primitive types (dictionaries, etc.)"""
    def __init__(self, name, properties={}):
        """Constructor."""
        # call parent function
        super(DbfSerialized, self).__init__(name, properties)
