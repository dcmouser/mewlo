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

    def startup(self, eventlist):
        """Any initial startup stuff to do?"""
        pass

    def remove_all(self):
        """Clear contents of settings."""
        self.settingdict = {}

    def remove_key(self, keyname):
        """Clear contents of one key."""
        del self.settingdict[keyname]

    def remove_subkey(self, keyname, keysubname):
        """Clear contents of one key."""
        del self.settingdict[keyname][keysubname]


    def merge_settings(self, settingstoadd):
        """Just merge in a new dicitonary into our main dictionary."""
        self.settingdict.update(settingstoadd)



    def merge_settings_key(self, keyname, settingstoadd):
        """Merge in a new dicitonary into our main dictionary at a specific root section (creating root section if needed)."""
        if not keyname in self.settingdict:
            self.settingdict[keyname] = settingstoadd
        else:
            # merge the new settings with old, e.g. union of arrays or dictionaries, etc
            self.settingdict[keyname].update(settingstoadd)


    def set_key(self, keyname, value):
        """Set and overwrite a value at a section, replacing whatever was there."""
        self.settingdict[keyname] = value


    def get_value(self, keyname, defaultval=None):
        """Lookup value from our settings dictionary and return it or default if not found."""
        return get_value_from_dict(self.settingdict, keyname, defaultval)


    def get_subvalue(self, keyname, keysubname, defaultval=None):
        """Lookup value from our settings dictionary at a certain root section, and return it or default if not found."""
        if (keyname in self.settingdict):
            if (keysubname in self.settingdict[keyname]):
                return self.settingdict[keyname][keysubname]
        return defaultval

    def set_subvalue(self, keyname, keysubname, val):
        """Set propery sub value."""
        settingstoadd = {keysubname:val}
        self.merge_settings_key(keyname,settingstoadd)


    def value_exists(self, keyname, keysubname=None):
        """Return true if the item existing in our settings dictionary (at specific root section if specified)."""
        if (keysubname == None):
            return (keyname in self.settingdict)
        if (not keyname in self.settingdict):
            return False
        return (keysubname in self.settingdict[keyname])



    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = " "*indent + "Settings ({0}):\n".format(self.__class__.__name__)
        indent += 1
        outstr += " "*indent + str(self.settingdict)+"\n"
        return outstr