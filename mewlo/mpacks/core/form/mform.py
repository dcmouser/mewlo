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
    DEF_GenericErrorKey = ''

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



    def add_fielderror(self, fieldname, errorstr):
        self.merge_errordict({fieldname: errorstr})


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



    def get_viewfilename(self, defaultval=None):
        """A form can store the view file it normally uses."""
        return self.__class__.viewfilename



    def set_values_from_dict(self, form_dict):
        """Set form values manually."""
        for key,val in form_dict.iteritems():
            if (hasattr(self,key)):
                ffield = getattr(self, key)
                ffield.data = val

    def set_onevalue(self, key, val):
        """Set one value key."""
        if (key==''):
            return
        if (hasattr(self,key)):
            ffield = getattr(self, key)
            ffield.data = val

    def get_val(self, key, defaultval=None):
        """Get one value."""
        if (hasattr(self,key)):
            ffield = getattr(self, key)
            return ffield.data
        return defaultval

    def get_val_nonblank(self, key, defaultval=None):
        """Get one value."""
        if (hasattr(self,key)):
            ffield = getattr(self, key)
            if ( (ffield.data != '') and (ffield.data != None) ):
                return ffield.data
        return defaultval


    def setfield_ifblank(self, key, val):
        """ Set value if empty."""
        ffield = getattr(self, key)
        if ((ffield.data == None) or (ffield.data == '')):
            ffield.data = val

    def hasfield(self, key):
        """Return True if the form has a field of this name."""
        return hasattr(self, key)







# helper derived WTForm classes





# from http://stackoverflow.com/questions/14874846/python-flask-wtforms-make-read-only-textfield
# for a dif approach see also https://github.com/kvesteri/wtforms-components/blob/master/wtforms_components/widgets.py
class DisabledStringField(StringField):
    def __call__(self, *args, **kwargs):
        kwargs.setdefault('disabled', True)
        kwargs.setdefault('size', 60)
        return super(DisabledStringField, self).__call__(*args, **kwargs)



class BigStringField(StringField):
    def __call__(self, *args, **kwargs):
        kwargs.setdefault('size', 60)
        return super(BigStringField, self).__call__(*args, **kwargs)
