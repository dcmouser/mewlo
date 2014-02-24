"""
form_resend_register_verification.py
This file contains login form stuff
"""


# mewlo imports
from mewlo.mpacks.core.form.mform import MewloForm, BigStringField


# library imports
from wtforms import Form, BooleanField, StringField, PasswordField, validators

# python imports







class MewloForm_Resend_Register_Verification_Known(MewloForm):

    email = BigStringField('Resend verification email to this address (change it if you wish)', [validators.Length(min=6, max=35)])
    #
    viewfilename = 'resend_register_verification_known.jn2'
    #
    def __init__(self, *args, **kwargs):
        # parent constructor
        super(MewloForm_Resend_Register_Verification_Known, self).__init__(*args, **kwargs)





class MewloForm_Resend_Register_Verification_Unknown(MewloForm):

    username = StringField('Signup username', [validators.Length(max=32)])
    email = BigStringField('Original or new email address', [validators.Length( max=35)])
    # if we disable password, client will be able to change email address for not-yet-verified usernames; this is ok as long as we dont ever let people login and do things while their email address is pending
    #password = PasswordField('Signup password (only needed if making changes)', [validators.Length(max=64)])
    #
    viewfilename = 'resend_register_verification_unknown.jn2'
    #
    def __init__(self, *args, **kwargs):
        # parent constructor
        super(MewloForm_Resend_Register_Verification_Unknown, self).__init__(*args, **kwargs)
