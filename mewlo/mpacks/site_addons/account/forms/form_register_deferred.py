"""
form_register_deferred.py
This file contains login form stuff
"""


# mewlo imports
from mewlo.mpacks.core.form.mform import MewloForm, BigStringField

# library imports
from wtforms import Form, BooleanField, StringField, PasswordField, validators

# python imports





class MewloForm_Register_Deferred(MewloForm):

    email = BigStringField('Email Address', [validators.Length(min=6, max=64)])

    viewfilename = 'register_deferred.jn2'

    def __init__(self, *args, **kwargs):
        # parent constructor
        super(MewloForm_Register_Deferred, self).__init__(*args, **kwargs)

