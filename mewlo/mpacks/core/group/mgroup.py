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





    def calc_nice_rbaclabel(self):
        """Return a nice label used for displaying rbac information."""
        return "group#{0}:{1}".format(self.id, self.groupname)


    def calc_nice_html_info(self):
        """Return nice html info for display."""
        return "{0}: {1}".format(self.id, self.groupname)





















    @classmethod
    def define_fields(cls, dbmanager):
        """This class-level function defines the database fields for this model -- the columns, etc."""

        # ATTN: UNFINISHED
        fieldlist = [
            # standard primary id number field
            mdbfield.DbfPrimaryId('id', {
                'label': "The primary key and id# for this group"
                }),
            mdbfield.DbfUsername('groupname', {
                'label': "Unique name for group"
                }),
            mdbfield.DbfLabelString('label', {
                'label': "Label for the group"
                }),
            mdbfield.DbfString('description', {
                'label': "Description for the group"
                }),
            # globally unique resource reference
            mdbmixins.dbfmixin_gobselfreference(),
            ]
        # standard objet deleted/enabled flags
        fieldlist += mdbmixins.dbfmixins_disabledelete()

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



    @classmethod
    def find_one_bynameorid(cls, nameorid):
        return cls.find_one_byflexibleid('groupname',nameorid)