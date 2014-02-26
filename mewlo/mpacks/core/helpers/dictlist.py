"""
dictlist.py
A combination dict and list that lets us use a hash and an ordered list
"""



# python imports
import inspect




class MDictList(object):
    """Dictionary-derived object with helper accessors."""

    def __init__(self):
        # dictionary
        self.itemdict = {}
        # list
        self.itemlist = []

    def append(self, key, val):
        """Add a new item to our list and dictionary."""
        thetuple = (key,val)
        self.itemlist.append( thetuple )
        self.itemdict[key]=val

    def lookup(self, key, defaultval = None):
        """Lookup value by key."""
        if (key in self.itemdict):
            return self.itemdict[key]
        return defaultval

    def get_tuplelist(self):
        """Just return the list of tuples."""
        return self.itemlist

    def get_itemlist(self):
        """Return list of 2nd elements of each tuple in list."""
        return [i[1] for i in self.itemlist]



    def dumps(self, prefixstr, indent, flag_newlineseparates):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = ""
        for tupe in self.itemlist:
            key = tupe[0]
            obj = tupe[1]
            if (flag_newlineseparates):
                outstr += '\n'
            outstr += " "*indent + "{0}{1}:\n".format(prefixstr, key)
            # if it's a class, look for classdumps(), otherwise dumps()
            if (inspect.isclass(obj)):
                if (hasattr(obj,'classdumps')):
                    outstr += obj.classdumps(indent+1)
                else:
                    outstr += " "*(indent+1) + str(obj)
            else:
                if (hasattr(obj,'dumps')):
                    outstr += obj.dumps(indent+1)
                else:
                    outstr += " "*(indent+1) + str(obj)
        return outstr







