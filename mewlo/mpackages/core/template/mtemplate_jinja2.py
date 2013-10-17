"""
mtemplate_jinja2.py
Derived template for jinja2.
"""

# mewlo imports
import mtemplate








class MewloTemplate_Jinja2(mtemplate.MewloTemplate):
    """The MewloTemplate class represents a single template file."""

    # class constants
    templatetype_id = 'jinja2'
    templatetype_extensions = ('.jn2',)

    def __init__(self, templatemanager):
        self.templatemanager = templatemanager
        self.jinja2_environement = None
        # parent function
        super(MewloTemplate_Jinja2, self).__init__()


    def load_from_file(self, filepath):
        """Load a template from a file."""
        self.filepath = filepath
        # get/make environment which uses our custom handler
        jinja2_environement = self.getmake_jinja2_environment(self.templatemanager)
        # load the template file
        self.template = jinja2_environement.get_template( filepath )


    def render_string(self, args):
        """Render template into a string and return string.  Use args dictionary to pass in values."""
        renderedtext = self.template.render(args)
        return renderedtext


    def getmake_jinja2_environment(self, templatemanager):
        """Class singleton reference to the jinja2 engine, created on first use."""
        if (self.jinja2_environement == None):
            # create it for first time, use our custom file loader which knows how to resolve view files
            import mjinja2_loader
            jinja2_templateLoader = mjinja2_loader.MewloJinja2Loader(templatemanager.mewlosite)
            self.jinja2_environement = mjinja2_loader.MewloJinja2Environment(templatemanager.mewlosite, loader=jinja2_templateLoader)
        return self.jinja2_environement



    @classmethod
    def dumps(cls, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object.
        Note that this is a CLASS function since we just want info about the class not a particular instance.
        """
        outstr = " "*indent + "MewloTemplate (" + cls.__name__ + ") reporting in.\n"
        return outstr

