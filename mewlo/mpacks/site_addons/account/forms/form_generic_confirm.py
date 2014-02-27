"""
form_generic_confirm.py
"""


# mewlo imports
from mewlo.mpacks.core.form.mform import MewloForm, BigStringField

# library imports
from wtforms import Form, BooleanField, StringField, PasswordField, validators

# python imports





class MewloForm_Generic_Confirm(MewloForm):

    viewfilename = 'form_generic_confirm.jn2'

    def __init__(self, *args, **kwargs):
        # parent constructor
        super(MewloForm_Generic_Confirm, self).__init__(*args, **kwargs)

