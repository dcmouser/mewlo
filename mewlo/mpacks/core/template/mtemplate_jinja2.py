"""
mtemplate_jinja2.py
Derived template for jinja2.
"""

# mewlo imports
import mtemplate


# jinja2 imports
import jinja2







class MewloTemplate_Jinja2(mtemplate.MewloTemplate):
    """The MewloTemplate class represents a single template file."""

    # class constants
    templatetype_id = 'jinja2'
    templatetype_extensions = ('.jn2',)

    def __init__(self, request, templatemanager):
        # parent function
        super(MewloTemplate_Jinja2, self).__init__(request, templatemanager)
        #
        self.filepath = None
        self.jinja2_environement = None
        #
        self.laterender_regex_search = r'\{\-\{(.*?)\}\-\}'
        self.laterender_regex_replace = r'{{\1}}'


    def load_from_file(self, filepath):
        """Load a template from a file."""
        self.filepath = filepath
        # get/make environment which uses our custom handler
        jinja2_environement = self.getmake_jinja2_environment(self.templatemanager, self.request)
        # load the template file
        self.template = jinja2_environement.get_template( filepath )


    def load_from_string(self, templatestring):
        """Load a template from a string."""
        self.filepath = None
        # get/make environment which uses our custom handler
        jinja2_environement = self.getmake_jinja2_environment(self.templatemanager, self.request)
        # load the template file
        self.template = jinja2_environement.from_string( templatestring )



    def getmake_jinja2_environment(self, templatemanager, request):
        """Class singleton reference to the jinja2 engine, created on first use."""
        # ATTN:!!!! THIS IS NOT A CLASS SINGLETON TODO:FIGUREOUT WHAT YOU REALLY WANT
        if (self.jinja2_environement == None):
            # create it for first time, use our custom file loader which knows how to resolve view files
            import mjinja2_loader
            # we use our custom loader
            jinja2_templateLoader = mjinja2_loader.MewloJinja2Loader(templatemanager.mewlosite, request)
            # by setting this to jinja2.StrictUndefined we cause an exception if an undefined variable is referenced in a template (default behavior is just insert a blank)
            jinja2_undefined = jinja2.StrictUndefined
            # create the environment
            self.jinja2_environement = mjinja2_loader.MewloJinja2Environment(templatemanager.mewlosite, request, loader=jinja2_templateLoader, undefined=jinja2_undefined)
        return self.jinja2_environement





    def render_string_internal(self, args):
        """Render template into a string and return string.  Use args dictionary to pass in values."""
        #print "ATTN: in render_string_internal with args={0}".format(str(args))
        renderedtext = self.template.render(args)
        return renderedtext
















    @classmethod
    def dumps(cls, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object.
        Note that this is a CLASS function since we just want info about the class not a particular instance.
        """
        outstr = " "*indent + "MewloTemplate (" + cls.__name__ + ") reporting in.\n"
        return outstr

