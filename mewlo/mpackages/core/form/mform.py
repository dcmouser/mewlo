"""
mform.py
This file contains base form class
"""


# mewlo imports


# python imports


# library imports
from wtforms import Form, BooleanField, StringField, validators





class MewloForm(Form):

    # class constants
    DEF_GenericErrorKey = 'GENERIC'

    class Meta:
        # Enable CSRF?
        csrf = False
        # Set the CSRF implementation
        #csrf_class = SomeCSRF
        # Some CSRF implementations need a secret key
        #csrf_secret = b'foobar'
        # Any other CSRF settings here.


    def __init__(self, *args, **kwargs):
        # parent constructor (important for wtform)
        super(MewloForm, self).__init__(*args, **kwargs)





    def add_genericerror(self, errorstr, separator = '\n'):
        """Add a generic error to form not tied to a field; this is our own kludge."""
        if (MewloForm.DEF_GenericErrorKey in self.errors):
            self.errors[MewloForm.DEF_GenericErrorKey] += separator + errorstr
        else:
            self.errors[MewloForm.DEF_GenericErrorKey] = errorstr

    def get_genericerrorstr(self, defaultval=None):
        """Return generic form error."""
        if (MewloForm.DEF_GenericErrorKey in self.errors):
            return self.errors[MewloForm.DEF_GenericErrorKey]
        return defaultval




    def merge_errordict(self, errordict):
        """Merge dictionary of errors into form."""
        if (errordict == None):
            return
        for key,val in errordict.iteritems():
            if (self.__contains__(key)):
                self.__getitem__(key).errors.append(val)
            else:
                if (key==MewloForm.DEF_GenericErrorKey):
                    self.add_genericerror(val)
        print "ERRORS NOW: "+str(self.errors)


