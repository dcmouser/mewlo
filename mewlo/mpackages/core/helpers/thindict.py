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
