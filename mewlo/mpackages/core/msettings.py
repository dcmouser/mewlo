# msettings.py
# This file contains classes to support hierarchical settings associates with sites




class MewloSettings(object):
    """
    The MewloSettings class stores a hierarchical dictionary of settings
    """

    def __init__(self):
        self.settingdict = {}
        pass


    def merge_settings(self, settingstoadd):
        self.settingdict.update(settingstoadd)

    def get_value(self, propertyname, defaultval=None):
        if (propertyname in self.settingdict):
            return self.settingdict[propertyname]
        return defaultval

    def get_sectionvalue(self, propertysection, propertyname, defaultval=None):
        if (propertysection in self.settingdict):
            if (propertyname in self.settingdict[propertysection]):
                return self.settingdict[propertysection][propertyname]
        return defaultval


    def debug(self, indentstr=""):
        outstr = indentstr+"Settings:\n"
        outstr += indentstr+str(self.settingdict)+"\n"
        return outstr