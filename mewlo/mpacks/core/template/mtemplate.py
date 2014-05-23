"""
mtemplate.py
This module contains classes and functions for interfacing with template system.
The MewloTemplateManager knows about all registered template types, and can find the right one to use given a template filename.
"""


# mewlo imports
from ..manager import manager
from ..constants.mconstants import MewloConstants as mconst


# python imports
import os.path
import re






class MewloTemplate(object):
    """The MewloTemplate class represents a single template file."""

    def __init__(self, request, templatemanager):
        self.request = request
        self.templatemanager = templatemanager
        self.filepath = None
        self.filecontents = None
        #
        self.laterender_regex_search = None
        self.laterender_regex_replace = None

    def load_from_file(self, filepath):
        """Load a template from a file."""
        self.filepath = filepath
        fp = open(filepath, 'r')
        self.filecontents = fp.read()
        fp.close()

    def load_from_string(self, templatestring):
        """Load a template from a string."""
        self.filecontents = templatestring


    def render_string(self, args={}):
        """Render template into a string and return string.  Use args dictionary to pass in values."""
        # first do the main work
        renderedtext = self.render_string_internal(args)
        # and now any LATE replacements -- this allows the rare case where we want to so some special replacements after the template has "executed"
        renderedtext = self.late_render_string(renderedtext, args)
        # return it
        return renderedtext


    def render_string_internal(self, args):
        """Render template into a string and return string.  Use args dictionary to pass in values."""
        raise Exception("ERROR: Base template invoked for function 'render_string_internal'.")

    def render_sections(self, args={}, required_sections=[]):
        """Render template broken into sections defined by @@SECTIONAME = headers
        In addition, any section named 'REM' is ignored.
        In addition, all section values are trimmed (stripped) of leading and trailing whitespace
        """
        # for safety, replace any @@ in args
        for (key,val) in args.iteritems():
            args[key] = args[key].replace('@@','__')
        # render to string
        renderedtext = self.render_string(args)
        # regex to use to grab sections
        patternregex = r'\@\@([a-zA-A]+)\s*\=\s*(.*?)\s*(?=\n\@\@|\Z)'
        # now get all matches, which should return tuples of the form (sectionname, sectiontext)
        allmatches = re.findall(patternregex, renderedtext, re.MULTILINE | re.DOTALL)
        # now partse them and fill dictionary
        sectionsout = {}
        for findtuple in allmatches:
            key = findtuple[0].strip()
            if (key != 'REM'):
                sectionsout[key] = findtuple[1].strip()
        #
        #print "ATTN: in with '{0}' and out with: {1}.".format(renderedtext,str(sectionsout))
        # check required sections
        for key in required_sections:
            if (not key in sectionsout):
                raise Exeception('Internal error, template is missing a required section ({0}): "{1}" (from {2}).'.format(key, str(sectionsout), self.filepath))
        return sectionsout



    def late_render_string(self, renderedtext, args={}):
        """Do late-rendering of an already rendered string."""
        # are there any things that need late rendering?
        if (self.laterender_regex_search):
            # try replacements
            (renderedtext, number_of_subs_made) = re.subn(self.laterender_regex_search, self.laterender_regex_replace, renderedtext)
            if (number_of_subs_made>0):
                #print "ATTN: late_render_string resulted in '{0}'.".format(renderedtext)
                # there were replacements, now re-render
                self.load_from_string(renderedtext)
                # non-recursive call (no more late expands)
                renderedtext = self.render_string_internal(args)
        # return it
        return renderedtext
























class MewloTemplateManager(manager.MewloManager):
    """The MewloTemplateManager class is the helper object which implements or interfaces to all template processing functionality."""

    # class constants
    description = "The template manager is used to help lookup view template files and serve them"
    typestr = "core"


    def __init__(self, mewlosite, debugmode):
        super(MewloTemplateManager,self).__init__(mewlosite, debugmode)
        self.needs_startupstages([mconst.DEF_STARTUPSTAGE_routestart])
        self.templatetypes = []




    def startup_prep(self, stageid, eventlist):
        """
        This is invoked by site strtup, for each stage specified in startup_stages_needed() above.
        """
        super(MewloTemplateManager,self).startup_prep(stageid, eventlist)
        if (stageid == mconst.DEF_STARTUPSTAGE_routestart):
            # register some built in template types
            import mtemplate_jinja2
            self.register_templateclass(mtemplate_jinja2.MewloTemplate_Jinja2)







    def from_file(self, request, filepath, templatetypeid=None):
        """Instantiate a template from a file."""
        templatelcass = self.lookup_templatetype_byfile(filepath, templatetypeid)
        template = templatelcass(request, self)
        filepath = request.resolve_filepath(filepath)
        template.load_from_file(filepath)
        return template



    def from_string(self, request, templatestring, templatetypeid):
        """Instantiate a template from a file."""
        templatelcass = self.lookup_templatetype_bytypeid(templatetypeid)
        template = templatelcass(request, self)
        template.load_from_string(templatestring)
        return template


    def register_templateclass(self, templateclass):
        """Register a template type."""
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
        outstr += self.dumps_description(indent+1)
        for templatetype in self.templatetypes:
            outstr += templatetype.dumps(indent+1)
        return outstr

