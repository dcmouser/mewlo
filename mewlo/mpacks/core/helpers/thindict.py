"""
thindict.py
Just a thinly expanded dict with some accessors to make life easier
"""



# python imports





class MThinDict(dict):
    """Dictionary-derived object with helper accessors."""

    def get_value(self, key, defaultval=None):
        if (key in self):
            return self[key]
        return defaultval


    def get_subvalue(self, key, subkey, defaultval=None):
        # two levels deep
        if (key in self):
            if (subkey in self[key]):
                return self[key][subkey]
        return defaultval


    def appendtovalue(self, key, val, separator='\n'):
        if (key in self):
            self[key] += separator + val
        else:
            self[key] = val