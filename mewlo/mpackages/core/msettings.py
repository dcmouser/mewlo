# msettings.py
# This file contains classes to support hierarchical settings associates with sites




class MewloSettings(object):
    """
    The MewloSettings class stores a hierarchical dictionary of settings
    """

    def __init__(self):
        self.settingdict = {}


    def merge_settings(self, settingstoadd):
        """Just merge in a new dicitonary into our main dictionary."""
        self.settingdict.update(settingstoadd)



    def merge_settings_atsection(self, sectionname, settingstoadd):
        """Merge in a new dicitonary into our main dictionary at a specific root section (creating root section if needed)."""
        if not sectionname in self.settingdict:
            self.settingdict[sectionname]=settingstoadd
        else:
            self.settingdict[sectionname].update(settingstoadd)



    def get_value(self, propertyname, defaultval=None):
        """Lookup value from our settings dictionary and return it or default if not found."""
        if (propertyname in self.settingdict):
            return self.settingdict[propertyname]
        return defaultval



    def get_sectionvalue(self, propertysection, propertyname, defaultval=None):
        """Lookup value from our settings dictionary at a certain root section, and return it or default if not found."""
        if (propertysection in self.settingdict):
            if (propertyname in self.settingdict[propertysection]):
                return self.settingdict[propertysection][propertyname]
        return defaultval



    def value_exists(self, propertyname, propertysection=None):
        """Return true if the item existing in our settings dictionary (at specific root section if specified)."""
        if (propertysection==None):
            return (propertyname in self.settingdict)
        return (propertyname in self.settingdict[propertysection])



    def debug(self, indentstr=""):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = indentstr+"MewloSettings:\n"
        outstr += indentstr+str(self.settingdict)+"\n"
        return outstr