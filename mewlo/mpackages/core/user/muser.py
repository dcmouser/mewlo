"""
muser.py

This is our database object base class.

"""




# mewlo imports
from ..database import mdbmodel
from ..database import mdbfield
from ..database import mdbmodelmixins



class MewloUser(mdbmodel.MewloDbModel):
    """User object / database model."""

    # class variables
    dbtablename = 'user'



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

        # TEST
        if (False):
            # add some fields at root level
            fieldlist += mdbmodelmixins.MewloDbModelMixin_AuthorTracker.get_dbfields()
        else:
            # add a special sub table that will contain some fields, using a class object attached to us
            subfields = mdbmodelmixins.MewloDbModelMixin_AuthorTracker.get_dbfields()
            fieldlist += cls.make_fieldset_dbobjectclass('atrack','author tracking object',dbmanager,subfields)


        #print "FIELDLIST FOR MUSER = " + str(fieldlist)

        cls.register_fieldlist(fieldlist)



