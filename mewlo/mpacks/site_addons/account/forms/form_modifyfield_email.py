"""
form_login.py
This file contains login form stuff
"""


# mewlo imports
from mewlo.mpacks.core.form.mform import MewloForm

# library imports
from wtforms import Form, BooleanField, StringField, PasswordField, validators

# python imports





class MewloForm_ModifyField_Email(MewloForm):

    email = StringField('New e-mail address', [validators.Length(min=6, max=35)])

    #
    viewfilename = 'generic_modify_field.jn2'

    def __init__(self, *args, **kwargs):
        # parent constructor
        super(MewloForm_ModifyField_Email, self).__init__(*args, **kwargs)

