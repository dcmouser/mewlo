"""
mdbpropertyset.py

This is our database object base class.

"""


# helper imports
from ..helpers import misc

# python imports
import pickle






class MewloDbPropertySet(MewloDbModel):
    """
    This class is used as a base class for adding to other MewloDbModel classes to manage sets of properties.
    Essentially the way this works is that if an extension wants to add properties (columns) to another model CLASS,
    it can do so by creating a PropertySet CLASS and adding that CLASS to the main model CLASS.
    This PropertySet will represent some lazy-loaded/saved properties.  Essentially this represents a "has-a" relationship
    with the main model class.
    """

    # ATTN: NOTE __INIT__ IS *NOT* CALLED WHEN INSTANTIATING MODELS VIA SQLALCHEMY ORM SO WE AVOID IT WHERE POSSIBLE






