"""
mdbsettings_package.py
Derived class for package database settings
"""


# helper imports
from ..database import mdbsettings, mdbmodel_settings


class MewloDbModel_Settings_Package(mdbmodel_settings.MewloDbModel_Settings):
    """See parent class."""
    # class variables
    dbtablename = 'settings_package2'
    dbschemaname = 'default'


class MewloSettingsDb_Package(mdbsettings.MewloSettingsDb):
    """See parent class."""
    # class vars
    dbmodelclass = MewloDbModel_Settings_Package


