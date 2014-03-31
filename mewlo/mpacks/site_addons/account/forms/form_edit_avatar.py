"""
form_edit_avatar.py
"""


# mewlo imports
from mewlo.mpacks.core.form.mform import MewloForm

# library imports
from wtforms import Form, BooleanField, StringField, PasswordField, validators

# python imports





class MewloForm_EditAvatar(MewloForm):

    #avatarfile = StringField('Avatar file', [validators.Length(min=3, max=132)])

    viewfilename = 'edit_avatar.jn2'

    def __init__(self, *args, **kwargs):
        # parent constructor
        super(MewloForm_EditAvatar, self).__init__(*args, **kwargs)

