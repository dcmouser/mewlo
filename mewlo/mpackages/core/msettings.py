# msettings.py
# This file contains classes to support hierarchical settings associates with sites




class MewloSettings(object):
    """
    The MewloSettings class stores a hierarchical dictionary of settings
    """

    def __init__(self):
        self.settingdict = {}


    def merge_settings(self, settingstoadd):
        self.settingdict.update(settingstoadd)

    def merge_settings_atsection(self, sectionname, settingstoadd):
        if not sectionname in self.settingdict:
            self.settingdict[sectionname]=settingstoadd
        else:
            self.settingdict[sectionname].update(settingstoadd)

    def get_value(self, propertyname, defaultval=None):
        if (propertyname in self.settingdict):
            return self.settingdict[propertyname]
        return defaultval

    def get_sectionvalue(self, propertysection, propertyname, defaultval=None):
        if (propertysection in self.settingdict):
            if (propertyname in self.settingdict[propertysection]):
                return self.settingdict[propertysection][propertyname]
        return defaultval

    def value_exists(self, propertyname, propertysection=None):
        if (propertysection==None):
            return (propertyname in self.settingdict)
        return (propertyname in self.settingdict[propertysection])


    def debug(self, indentstr=""):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = indentstr+"MewloSettings:\n"
        outstr += indentstr+str(self.settingdict)+"\n"
        return outstr