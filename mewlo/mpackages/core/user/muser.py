"""
muser.py

This model represents users.

"""




# mewlo imports
from ..database import mdbmodel
from ..database import mdbfield
from ..database import mdbmixins
from ..database import mdbmodel_fieldset



class MewloUser(mdbmodel.MewloDbModel):
    """User object / database model."""

    # class variables
    dbtablename = 'user'
    #
    flag_mixin_atroot = False




    def init(self):
        """Manually called init on manually created new instances."""
        self.gobify(self.__class__.__name__)




    @classmethod
    def definedb(cls, dbmanager):
        """This class-level function defines the database fields for this model -- the columns, etc."""
        # define fields list

        # ATTN: UNFINISHED
        fieldlist = [
            # standard primary id number field
            mdbfield.DbfPrimaryId('id', {
                'label': "The primary key and id# for this user"
                }),
            # globally unique resource reference
            mdbmixins.Dbf_GobReference('user'),
            ]

        # add fieldlist to hash
        cls.hash_fieldlist(fieldlist)







    @classmethod
    def create_helpermodels(cls, dbmanager):
        """Create and register with the dbmanager any model classes that this class uses as helpers."""
        subfields = mdbmixins.MewloDbModelMixin_AuthorTracker.get_dbfields()
        if (cls.flag_mixin_atroot):
            # prepare extra fields that will be added at root; this doesnt actually create any helper models
            cls.extend_extrafields(subfields)
        else:
            # add a special sub table that will contain some fields, using a helper class object attached to us
            # create (AND REGISTER) the new helper object

            cls.extend_extrafields(mdbmodel_fieldset.MewloDbFieldset.make_fieldset_dbobjectclass(cls,'atrack','author tracking object',cls.dbtablename,dbmanager,subfields))



