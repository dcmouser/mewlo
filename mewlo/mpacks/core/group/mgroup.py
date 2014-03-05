"""
mgroup.py

This model represents user groups

"""




# mewlo imports
from ..database import mdbmodel
from ..database import mdbfield
from ..database import mdbmixins
from ..database import mdbmodel_fieldset
from ..database import mdbmodel_relation
from ..user import muser



class MewloGroup(mdbmodel.MewloDbModel):
    """Group object / database model."""

    # class variables
    dbtablename = 'ugroup'
    #
    flag_mixin_atroot = False


    def __init__(self):
        self.init()

    def init(self):
        """Manually called init on manually created new instances."""
        # IMPORTANT: create a new gob database model entry for this object
        self.gobify()



    @classmethod
    def define_fields(cls, dbmanager):
        """This class-level function defines the database fields for this model -- the columns, etc."""

        # ATTN: UNFINISHED
        fieldlist = [
            # standard primary id number field
            mdbfield.DbfPrimaryId('id', {
                'label': "The primary key and id# for this group"
                }),
            mdbfield.DbfString('groupname', {
                'label': "Unique name for group"
                }),
            # globally unique resource reference
            mdbmixins.dbfmixin_gobselfreference(),

            ]

        return fieldlist




    @classmethod
    def create_prerequisites(cls, dbmanager):
        """Create and register with the dbmanager any prerequisites that this class uses."""
        subfields = mdbmixins.dbfmixins_authortracker()
        if (cls.flag_mixin_atroot):
            # prepare extra fields that will be added at root; this doesnt actually create any helper models
            cls.extend_fields(subfields)
        else:
            # add a special sub table that will contain some fields, using a helper class object attached to us
            # create (AND REGISTER) the new helper object
            backrefname = cls.get_dbtablename_pure()
            mdbmodel_fieldset.MewloDbFieldset.make_fieldset_dbobjectclass(cls,'tracking','author tracking object',backrefname,dbmanager,subfields)



