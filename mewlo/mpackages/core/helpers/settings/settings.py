"""
settings.py
This file contains classes to support hierarchical settings.

We really don't do anything fancy here -- in fact some of it is a bit ugly and could use rewriting.

Essentially we are just maintaining a hierarchical dictionary with some support functions to ease access.

"""


# helper imports
from ..misc import get_value_from_dict



class Settings(object):
    """
    The MewloSettings class stores a hierarchical dictionary of settings
    """

    def __init__(self):
        self.settingdict = {}


    def remove_all(self):
        """Clear contents of settings."""
        self.settingdict = {}

    def remove_property(self, propertyname):
        """Clear contents of one property."""
        del self.settingdict[propertyname]


    def merge_settings(self, settingstoadd):
        """Just merge in a new dicitonary into our main dictionary."""
        self.settingdict.update(settingstoadd)



    def merge_settings_property(self, propertyname, settingstoadd):
        """Merge in a new dicitonary into our main dictionary at a specific root section (creating root section if needed)."""
        if not propertyname in self.settingdict:
            self.settingdict[propertyname] = settingstoadd
        else:
            # merge the new settings with old, e.g. union of arrays or dictionaries, etc
            self.settingdict[propertyname].update(settingstoadd)


    def set_property(self, propertyname, value):
        """Set and overwrite a value at a section, replacing whatever was there."""
        self.settingdict[propertyname] = value


    def get_value(self, propertyname, defaultval=None):
        """Lookup value from our settings dictionary and return it or default if not found."""
        return get_value_from_dict(self.settingdict, propertyname, defaultval)


    def get_subvalue(self, propertyname, propertysubname, defaultval=None):
        """Lookup value from our settings dictionary at a certain root section, and return it or default if not found."""
        if (propertyname in self.settingdict):
            if (propertysubname in self.settingdict[propertyname]):
                return self.settingdict[propertyname][propertysubname]
        return defaultval



    def value_exists(self, propertyname, propertysubname=None):
        """Return true if the item existing in our settings dictionary (at specific root section if specified)."""
        if (propertysubname == None):
            return (propertyname in self.settingdict)
        if (not propertyname in self.settingdict):
            return False
        return (propertysubname in self.settingdict[propertyname])



    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = " "*indent + "MewloSettings:\n"
        indent += 1
        outstr += " "*indent + str(self.settingdict)+"\n"
        return outstr