"""
mtesting.py
This file contains classes to help test mewlo
"""






class MewloTester(object):
    """
    The MewloSite class represents a single "site" that handles requests.
    Typically you will only have one site running.
    """


    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = " "*indent + "MewloTester reporting in.\n"
        return outstr

