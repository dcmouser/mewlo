"""
mdbmodel_relation.py

This file contains some common model relation helpers.

"""


# helper imports
import mdbmodel
import mdbfield






class MewloDbRelationModel(mdbmodel.MewloDbModel):
    """A relation object helper."""
    pass






class MewloDbRelationModel_SimpleMtoN(MewloDbRelationModel):
    """A relation object helper."""
    pass


    @classmethod
    def set_sideclasses(cls, leftclass, rightclass):
        cls.leftclass = leftclass
        cls.rightclass = rightclass


    @classmethod
    def define_fields(cls, dbmanager):
        """This class-level function defines the database fields for this model."""

        # starting field list is just primary id
        fieldlist = [
            # standard primary id number field
            mdbfield.DbfPrimaryId('id', {
                'label': "The primary key and id# for this row"
                }),
            # foreign key to left
            mdbfield.DbfForeignKey(cls.leftclass.get_dbtablename()+'_id', {
                'label': "Left hand side of association ({0})".format(cls.leftclass.__name__),
                'foreignkeyname': cls.leftclass.get_dbtablename()+'.id',
                }),
            # foreign key to right
            mdbfield.DbfForeignKey(cls.rightclass.get_dbtablename()+'_id', {
                'label': "Right hand side of association ({0})".format(cls.rightclass.__name__),
                'foreignkeyname': cls.rightclass.get_dbtablename()+'.id',
                }),
            ]

        return fieldlist






    @classmethod
    def make_dbobjectclass(cls, leftclass, rightclass, dbmanager):
        """Make a derived class."""

        ownerclass = leftclass
        basesubclass = cls
        fieldlist = []

        # ok dynamically create a new class for this purpose
        subclassname = leftclass.__name__ + '_' + rightclass.__name__ + '_mnsimple'
        subclasstablename = leftclass.get_dbtablename()+'_'+rightclass.get_dbtablename()+'_mnsimple'
        # NOTE: we call create_derived_dbmodelclass() to dynamically on the fly create a new model class based on an existing one, but with unique table, etc.
        subclass = dbmanager.create_derived_dbmodelclass(ownerclass, basesubclass, subclassname, subclasstablename)

        # now set some values
        subclass.set_sideclasses(leftclass,rightclass)

        # and now register the subclass with the manager
        dbmanager.register_modelclass(ownerclass, subclass)

        # and now we want to add fields to left and right class so they map to each other through us
        leftcollectionname = leftclass.get_dbtablename()+'s'
        rightcollectionname = rightclass.get_dbtablename()+'s'
        leftfields = [
            mdbfield.DbfNtoM_SimpleRelation(rightcollectionname,{
                'associationclass':subclass,
                'otherclass':rightclass,
                'backrefname':leftcollectionname}),
            ]
        leftclass.extend_fields(leftfields)

        # return the newly created class
        return subclass
























class MewloDbRelationModel_FullMtoN(MewloDbRelationModel):
    """A relation object helper."""
    pass


    @classmethod
    def set_sideclasses(cls, leftclass, rightclass):
        cls.leftclass = leftclass
        cls.rightclass = rightclass


    @classmethod
    def define_fields(cls, dbmanager):
        """This class-level function defines the database fields for this model."""
        #
        leftcollectionname = cls.leftclass.get_dbtablename()+'s'
        rightitemname = cls.rightclass.get_dbtablename()
        rightcollectionname = cls.rightclass.get_dbtablename()+'s'
        leftitemname = cls.leftclass.get_dbtablename()


        # starting field list is just primary id
        fieldlist = [
            # standard primary id number field
            mdbfield.DbfPrimaryId('id', {
                'label': "The primary key and id# for this row"
                }),
            # foreign key to left
            mdbfield.DbfForeignKey(cls.leftclass.get_dbtablename()+'_id', {
                'label': "Left hand side of association ({0})".format(cls.leftclass.__name__),
                'foreignkeyname': cls.leftclass.get_dbtablename()+'.id',
                }),
            # foreign key to right
            mdbfield.DbfForeignKey(cls.rightclass.get_dbtablename()+'_id', {
                'label': "Right hand side of association ({0})".format(cls.rightclass.__name__),
                'foreignkeyname': cls.rightclass.get_dbtablename()+'.id',
                }),

            # ok now this association class is like a 1-N-1 relationship between the two classes

            # add a relationship from this intermediate association to the right class and back
            mdbfield.DbfNtoM_SimpleRelation(rightitemname,{
                'associationclass':None,
                'otherclass':cls.rightclass,
                'backrefname':leftcollectionname}),

            # now we try doing the other side (and back)
            # ATTN: now that we have moved this code, the direction of the backref is changed -- we should make sure there arent unintended consequences
            mdbfield.DbfNtoM_SimpleRelation(leftitemname,{
                'associationclass':None,
                'otherclass':cls.leftclass,
                'backrefname':rightcollectionname}),
            ]

        return fieldlist




    @classmethod
    def make_dbobjectclass(cls, leftclass, rightclass, dbmanager):
        """Make a derived class."""

        ownerclass = leftclass
        basesubclass = cls
        fieldlist = []

        # ok dynamically create a new class for this purpose
        subclassname = leftclass.__name__ + '_' + rightclass.__name__ + '_mnfull'
        subclasstablename = leftclass.get_dbtablename()+'_'+rightclass.get_dbtablename()+'_mnfull'
        # NOTE: we call create_derived_dbmodelclass() to dynamically on the fly create a new model class based on an existing one, but with unique table, etc.
        subclass = dbmanager.create_derived_dbmodelclass(ownerclass, basesubclass, subclassname, subclasstablename)

        # now set some values
        subclass.set_sideclasses(leftclass,rightclass)

        # and now register the subclass with the manager
        dbmanager.register_modelclass(ownerclass, subclass)


# ATTN: we try creating this in relation class now (11/6/13)
        # and now we want to add fields to left and right class so they map to each other through us
        # so this field we add to our LEFT class, with a 1-N relationship with out association class, but calling it by name of right hand set
        # in the created association class we will add to the RIGHT class
#        leftitemname = leftclass.get_dbtablename()
#        rightcollectionname = rightclass.get_dbtablename()+'s'
#        leftfields = [
#            mdbfield.DbfNtoM_SimpleRelation(rightcollectionname,{
#                'associationclass':None,
#                'otherclass':subclass,
#                'backrefname':leftitemname}),
#            ]
#        leftclass.extend_extrafields(leftfields)
# ATTN: now that we have moved this code, the direction of the backref is changed -- we should make sure there arent unintended consequences

        # save subclass INSIDE leftclass so we can refer to it later; useful so we can look up the class of the association
        leftclass.save_friendclass('AssociationRelation_'+rightclass.get_dbtablename(),subclass)

        # return the newly created class
        return subclass




