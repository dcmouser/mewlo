"""
mtemplate_jinja2.py
Derived template for jinja2.
"""

# mewlo imports
import mtemplate


class MewloTemplate_Jinja2(mtemplate.MewloTemplate):
    """The MewloTemplate class represents a single template file."""

    # class vars
    # ATTN: to improve
    # hey, you know what's not cool? the fact that the first thing we discover about jinja2 is that it's absolutely fucking retarded about windows paths
    #templateLoader = jinja2.FileSystemLoader( searchpath='' )
    #templateEnv = jinja2.Environment( loader=templateLoader )
    templatetype_id = 'jinja2'
    templatetype_extensions = ('.jn2',)


    def __init__(self):
        # parent function
        super(MewloTemplate_Jinja2,self).__init__()


    def load_from_file(self, filepath):
        """Load a template from a file."""
        self.filepath = filepath

        # library imports
        import jinja2

        if (False):
            # fucking retarded jinja2 absolutely refuses to let me pass absolute path to template file and create environment once
            self.templateLoader = jinja2.FileSystemLoader( searchpath='' )
            self.templateEnv = jinja2.Environment( loader=self.templateLoader )
            self.template = self.templateEnv.get_template( filepath )
        else:
            # so instead we have to create a filesystemload and environment on EACH call -- thank you
            import os
            (dirpath, fname) = os.path.split(filepath)
            self.templateLoader = jinja2.FileSystemLoader( searchpath=dirpath )
            self.templateEnv = jinja2.Environment( loader=self.templateLoader )
            self.template = self.templateEnv.get_template( fname )




    def render_string(self, args):
        """Render template into a string and return string.  Use args dictionary to pass in values."""
        renderedtext = self.template.render(args)
        return renderedtext





    @classmethod
    def dumps(cls, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = " "*indent + "MewloTemplate (" + cls.__name__ + ") reporting in.\n"
        return outstr

