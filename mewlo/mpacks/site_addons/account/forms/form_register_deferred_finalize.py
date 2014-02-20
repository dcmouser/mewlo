"""
form_register_deferred_finalize.py
This file contains login form stuff
"""


# mewlo imports
from mewlo.mpacks.core.form.mform import MewloForm, DisabledStringField, BigStringField

# library imports
from wtforms import Form, BooleanField, StringField, PasswordField, HiddenField, validators, widgets

# python imports





class MewloForm_Register_Deferred_Finalize(MewloForm):

    username = StringField('Username', [validators.Length(min=3, max=32)])
    password = PasswordField('Password', [validators.Length(min=3, max=64)])
    email = DisabledStringField('Email Address')
    accept_rules = BooleanField('I accept the site rules', [validators.InputRequired()])
    #
    code = HiddenField('Verification code', [])
    #
    viewfilename = 'register_deferred_finalize.jn2'

    def __init__(self, *args, **kwargs):
        # parent constructor
        super(MewloForm_Register_Deferred_Finalize, self).__init__(*args, **kwargs)

