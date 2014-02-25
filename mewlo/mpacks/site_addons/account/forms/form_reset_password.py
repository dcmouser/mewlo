"""
form_reset_password.py
"""


# mewlo imports
from mewlo.mpacks.core.form.mform import MewloForm, BigStringField


# library imports
from wtforms import Form, BooleanField, StringField, PasswordField, HiddenField, validators

# python imports






class MewloForm_Send_Reset_Password(MewloForm):

    username = StringField('Username', [validators.Length(max=32)])
    email = BigStringField('or E-mail address', [validators.Length( max=35)])
    #
    viewfilename = 'reset_password_send.jn2'
    #
    def __init__(self, *args, **kwargs):
        # parent constructor
        super(MewloForm_Send_Reset_Password, self).__init__(*args, **kwargs)




class MewloForm_Submit_Reset_Password(MewloForm):

    password = PasswordField('New password', [validators.Length(min=3, max=64)])
    code = HiddenField('Verification code', [])
    #
    viewfilename = 'reset_password_submit.jn2'

    def __init__(self, *args, **kwargs):
        # parent constructor
        super(MewloForm_Submit_Reset_Password, self).__init__(*args, **kwargs)



