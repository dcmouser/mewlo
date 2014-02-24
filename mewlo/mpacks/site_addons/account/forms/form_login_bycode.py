"""
form_login_bycode.py
This file contains login form stuff
"""


# mewlo imports
from mewlo.mpacks.core.form.mform import MewloForm

# library imports
from wtforms import StringField, validators

# python imports





class MewloForm_Login_ByCode(MewloForm):

    code = StringField('Code', [validators.Length(min=3, max=32)])
    viewfilename = 'login_bycode.jn2'

    def __init__(self, *args, **kwargs):
        # parent constructor
        super(MewloForm_Login_ByCode, self).__init__(*args, **kwargs)

