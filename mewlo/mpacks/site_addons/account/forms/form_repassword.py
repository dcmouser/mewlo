"""
form_repassword.py
This file contains login form stuff
"""


# mewlo imports
from mewlo.mpacks.core.form.mform import MewloForm

# library imports
from wtforms import Form, BooleanField, StringField, PasswordField, validators

# python imports





class MewloForm_RePassword(MewloForm):

    password = PasswordField('Password', [validators.Length(min=3, max=64)])

    #
    viewfilename = 'repassword.jn2'

    def __init__(self, *args, **kwargs):
        # parent constructor
        super(MewloForm_RePassword, self).__init__(*args, **kwargs)

