"""
mtemplate.py
This module contains classes and functions for interfacing with template system.
The MewloTemplateManager knows about all registered template types, and can find the right one to use given a template filename.
"""


# mewlo imports
from ..manager import manager


# python imports
import os.path







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


    def render_string(self, args={}):
        """Render template into a string and return string.  Use args dictionary to pass in values."""
        raise Exception("Base template invoked for function 'render_string'.")









class MewloTemplateManager(manager.MewloManager):
    """The MewloTemplateManager class is the helper object which implements or interfaces to all template processing functionality."""

    def __init__(self):
        super(MewloTemplateManager,self).__init__()
        self.templatetypes = []

    def startup(self, mewlosite, eventlist):
        super(MewloTemplateManager,self).startup(mewlosite,eventlist)
        # register some built in template types
        import mtemplate_jinja2
        self.register_templateclass(mtemplate_jinja2.MewloTemplate_Jinja2)

    def shutdown(self):
        super(MewloTemplateManager,self).shutdown()




    def from_file(self, filepath, templatetypeid=None):
        """Instantiate a template from a file."""
        filepath = self.mewlosite.resolve(filepath)
        templatelcass = self.lookup_templatetype_byfile(filepath, templatetypeid)
        template = templatelcass(self)
        template.load_from_file(filepath)
        return template


    def register_templateclass(self, templateclass):
        """ Register a template type."""
        self.templatetypes.append(templateclass)


    def lookup_templatetype_byfile(self, filepath, templatetypeid):
        """Lookup a registered template type."""
        if (templatetypeid!=None):
            return self.lookup_templatetype_bytypeid(templatetypeid)
        # get extension
        for templatetype in self.templatetypes:
            if (self.filename_endsin_list(filepath,templatetype.templatetype_extensions)):
                return templatetype
        # failed to find
        raise Exception("Template typeclass lookup by filename (extenstion) for file '{0}' failed to find a matching template typeclass.".format(filepath))


    def lookup_templatetype_bytypeid(self, templatetypeid):
        """Lookup a registered template type."""
        for templatetype in self.templatetypes:
            if (templatetype.templatetype_id == templatetypeid):
                return templatetype
        # failed to find
        raise Exception("Template typeclass lookup by id of '{0}' failed.".format(templatetypeid))


    def filename_endsin_list(self, filepath, endpatternlist):
        """Return True if the filepath ends in one of the items in endpatternlist.  Note this is different from checking the EXTENSION since here we can match on "*_jinja2.html" for example."""
        return (filepath.endswith(endpatternlist))


    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = " "*indent + "MewloTemplateManager (" + self.__class__.__name__ + ") reporting in:\n"
        for templatetype in self.templatetypes:
            outstr += templatetype.dumps(indent+1)
        return outstr

