"""
muser.py

This is our database object base class.

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
    extrafields = []


    @classmethod
    def definedb(cls, dbmanager):
        """This class-level function defines the database fields for this model -- the columns, etc."""
        # define fields list

        # ATTN: UNFINISHED
        fieldlist = [
            # standard primary id number field
            mdbfield.DbfPrimaryId('id', {
                'label': "The primary key and id# for this row"
                }),
            ]

        # add extrafields
        fieldlist.extend(cls.extrafields)

        # add fieldlist to hash
        cls.hash_fieldlist(fieldlist)




    @classmethod
    def create_helper_modelclasses(cls, dbmanager):
        """Create and register with the dbmanager any model classes that this class uses as helpers."""
        if (cls.flag_mixin_atroot):
            # prepare extra fields that will be added at root
            cls.extrafields = mdbmixins.MewloDbModelMixin_AuthorTracker.get_dbfields()
        else:
            # add a special sub table that will contain some fields, using a class object attached to us
            subfields = mdbmixins.MewloDbModelMixin_AuthorTracker.get_dbfields()
            # create (AND REGISTER) the new helper object
            cls.extrafields = mdbmodel_fieldset.MewloDbFieldset.make_fieldset_dbobjectclass(cls,'atrack','author tracking object','user',dbmanager,subfields)



