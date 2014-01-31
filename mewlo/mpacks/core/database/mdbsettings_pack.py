"""
mdbsettings_pack.py
Derived class for pack database settings
"""


# helper imports
from ..database import mdbsettings, mdbmodel_settings


class MewloDbModel_Settings_Pack(mdbmodel_settings.MewloDbModel_Settings):
    """See parent class."""
    # class variables
    dbtablename = 'settings_pack2'
    dbschemaname = 'default'


class MewloSettingsDb_Pack(mdbsettings.MewloSettingsDb):
    """See parent class."""
    # class vars
    dbmodelclass = MewloDbModel_Settings_Pack


