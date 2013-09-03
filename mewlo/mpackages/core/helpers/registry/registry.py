"""
registry.py
This module contains classes and functions for managing a component/service registry.

"""


# helper imports
from ..misc import does_dict_filter_match

# python imports







class Component(object):
    """A component object that can be added to the ComponentRegsitry."""

    def __init__(self, features, obj):
        """Constructor."""
        # init
        self.features = features
        self.obj = obj


    def does_match_feature_filter(self, feature_filter):
        """Return True if feature_filter matches features of the component."""
        return does_dict_filter_match(self.features, feature_filter)



    def dumps(self, indent=0):
        """Debug information."""
        outstr = " "*indent + "Component (" + self.__class__.__name__  + ") reporting in.\n"
        indent += 1
        outstr += " "*indent + "features: "+str(self.features)+"\n"
        outstr += " "*indent + "obj: "+str(self.obj)+"\n"
        if (hasattr(self.obj,'dumps')):
            outstr += self.obj.dumps(indent+1)
        return outstr









class ComponentRegistry(object):
    """The component registry."""

    def __init__(self):
        """Constructor."""
        # init
        self.components = []




    def register_component(self, component):
        """
        Add a component to the registry.
        """
        self.components.append(component)



    def find_all_matching_components(self, feature_filter):
        """
        Find matching components using the feature_filter passed.
        """
        # ATTN: eventually we will want to do this more efficently or flexibly
        # walk components and find matches
        matches = []
        for component in self.components:
            if (component.does_match_feature_filter(feature_filter)):
                matches.append(component)
        return matches


    def find_one_matching_component(self, feature_filter, flag_errorifnotfound = True, flag_errorifmorethanone = True):
        """
        Find one and only one matching components using the feature_filter passed.
        """
        matches = self.find_all_matching_components(feature_filter)
        if (len(matches)==0):
            if (flag_errorifnotfound):
                raise Exeception("Component matching feature filter [" + str(feature_filter) + "] not found.")
            return None
        if (len(matches)>1 and flag_errorifmorethanone):
            raise Exeception("More than one component matching feature filter [" + str(feature_filter) + "] was found, but assertion was that there should only be one.")
        # return the first match
        return matches[0]




    def dumps(self, indent=0):
        """Debug information."""
        outstr = " "*indent + "Component Registry (" + self.__class__.__name__ + ") reporting in.\n"
        indent += 1
        outstr += " "*indent + "Registered Components: "+str(len(self.components))+"\n"
        for component in self.components:
            outstr+=component.dumps(indent+1)
        return outstr


