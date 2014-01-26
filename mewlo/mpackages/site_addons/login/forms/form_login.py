"""
form_login.py
This file contains login form stuff
"""


# mewlo imports
from mewlo.mpackages.core.form.mform import MewloForm

# library imports
from wtforms import Form, BooleanField, StringField, PasswordField, validators

# python imports





class MewloForm_Login(MewloForm):

    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [validators.Length(min=6, max=35)])
    #email = StringField('Email Address', [validators.Length(min=6, max=35)])
    #accept_rules = BooleanField('I accept the site rules', [validators.InputRequired()])

    def __init__(self, *args, **kwargs):
        # parent constructor
        super(MewloForm_Login, self).__init__(*args, **kwargs)

