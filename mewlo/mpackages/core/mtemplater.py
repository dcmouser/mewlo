"""
mtemplate.py
This module contains classes and functions for interfacing with template system.
"""


# helper imports


# python imports
import os.path

# library imports
import jinja2






class MewloTemplate(object):
    """The MewloTemplate class represents a single template file."""

    def __init__(self):
        self.filepath = None
        self.filecontents = None


    def load_from_file(self, filepath):
        """Load a template from a file."""
        self.filepath = filepath
        fp = open(filepath, 'r')
        self.filecontents = fp.read()
        fp.close()


    def render_string(self, args):
        """Render template into a string and return string.  Use args dictionary to pass in values."""
        raise Exception("Base template invoked for function 'render_string'.")




class MewloTemplate_Jinja2(object):
    """The MewloTemplate class represents a single template file."""

    # class vars
    # ATTN: to improve
    # hey, you know what's not cool? the fact that the first thing we discover about jinja2 is that it's absolutely fucking retarded about windows paths
    #templateLoader = jinja2.FileSystemLoader( searchpath='' )
    #templateEnv = jinja2.Environment( loader=templateLoader )

    def __init__(self):
        # parent function
        super(MewloTemplate_Jinja2,self).__init__()


    def load_from_file(self, filepath):
        """Load a template from a file."""
        self.filepath = filepath

        if (False):
            # fucking retarded jinja2 absolutely refuses to let me pass absolute path to template file and create environment once
            self.templateLoader = jinja2.FileSystemLoader( searchpath='' )
            self.templateEnv = jinja2.Environment( loader=self.templateLoader )
            self.template = self.templateEnv.get_template( filepath )
        else:
            # so instead we have to create a filesystemload and environment on EACH call -- thank you
            (dirpath, fname) = os.path.split(filepath)
            self.templateLoader = jinja2.FileSystemLoader( searchpath=dirpath )
            self.templateEnv = jinja2.Environment( loader=self.templateLoader )
            self.template = self.templateEnv.get_template( fname )




    def render_string(self, args):
        """Render template into a string and return string.  Use args dictionary to pass in values."""
        renderedtext = self.template.render(args)
        return renderedtext









class MewloTemplater(object):
    """The MewloTemplater class is the helper object which implements or interfaces to all template processing functionality."""

    def __init__(self, mewlosite):
        self.mewlosite = mewlosite

    def startup(self, eventlist):
        pass

    def shutdown(self):
        pass


    def from_file(self, filepath):
        """Instantiate a template from a file."""
        filepath = self.mewlosite.resolvealias(filepath)
        template = MewloTemplate_Jinja2()
        template.load_from_file(filepath)
        return template


    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = " "*indent + "MewloTemplater (" + self.__class__.__name__ + ") reporting in.\n"
        return outstr