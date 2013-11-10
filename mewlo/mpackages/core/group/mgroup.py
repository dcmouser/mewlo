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


    def init(self):
        """Manually called init on manually created new instances."""
        self.gobify()



    @classmethod
    def define_fields(cls, dbmanager):
        """This class-level function defines the database fields for this model -- the columns, etc."""
        # define fields list

        # ATTN: UNFINISHED
        fieldlist = [
            # standard primary id number field
            mdbfield.DbfPrimaryId('id', {
                'label': "The primary key and id# for this group"
                }),
            # globally unique resource reference
            mdbmixins.Dbf_GobReference('user'),
            ]

        return fieldlist




    @classmethod
    def create_helpermodels(cls, dbmanager):
        """Create and register with the dbmanager any model classes that this class uses as helpers."""
        subfields = mdbmixins.MewloDbModelMixin_AuthorTracker.get_dbfields()
        if (cls.flag_mixin_atroot):
            # prepare extra fields that will be added at root; this doesnt actually create any helper models
            cls.extend_fields(subfields)
        else:
            # add a special sub table that will contain some fields, using a helper class object attached to us
            # create (AND REGISTER) the new helper object
            cls.extend_fields(mdbmodel_fieldset.MewloDbFieldset.make_fieldset_dbobjectclass(cls,'atrack','author tracking object',cls.dbtablename,dbmanager,subfields))

        # create a helper class that acts as a many-to-many association table
#        mdbmodel_relation.MewloDbRelationModel_SimpleMtoN.make_dbobjectclass(cls, muser.MewloUser, dbmanager)
#        mdbmodel_relation.MewloDbRelationModel_FullMtoN.make_dbobjectclass(muser.MewloUser, MewloGroup, dbmanager)
        # ATTN: this was a test -- we now use roles for this and create elsewhere


