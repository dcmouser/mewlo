"""
mregistry.py
This module contains classes and functions for managing a component/service registry.

Here's how it works:

A ComponentRegistry object holds a list of "Component" objects.
A Component object is simply a thin wrapper around an arbitrary object, annotating it with a "feature
 dictionary.
This feature dictionary is then used by consumers of the ComponentRegistry, so that they may ask the
 ComponentRegistry to look up a component that possesses certain features.
Everything else, from the class of the wrapped Component objects to the kinds of features, is all handled by convention.

This is a very minimalist system for registering objects and making it possible for them to be discovered by other parts of code.

For an alternate way of supporting discovery of and communication between objects, one could use the Signal system.

Some fields for the Component "feature" dictionary:
    * 'name' - should always be specified to aid in debugging (need not be unique)
    * 'version' - integer numeric version useful for filtering and compatibility checks
    * ATTN: TODO add more

How to use the feature filter to look up matching components:
    * ATTN: TODO - We use a generic filtering system (see does_dict_filter_match(); it's also used for log messages).

"""


# mewlo imports
from ..helpers.misc import does_dict_filter_match
from ..manager import manager

# python imports
import inspect






class MewloComponent(object):
    """A component object that can be added to the ComponentRegsitry."""

    def __init__(self, id, owner, features, obj):
        """Constructor."""
        # init
        self.id = id
        self.owner = owner
        self.features = features
        self.obj = obj
        # add id to features
        self.features['id'] = id


    def startup(self):
        #print "**** IN COMPONENT STARTUP ****"
        pass

    def shutdown(self):
        #print "**** IN COMPONENT SHUTDOWN ****"
        pass


    def get_features(self):
        """We use a function here in case subclass wants to override."""
        return self.features


    def does_match_feature_filter(self, feature_filter):
        """Return True if feature_filter matches features of the component."""
        return does_dict_filter_match(self.get_features(), feature_filter)



    def dumps(self, indent=0):
        """Debug information."""
        outstr = " "*indent + "Component (" + self.__class__.__name__  + ") reporting in.\n"
        indent += 1
        outstr += " "*indent + "features: "+str(self.get_features())+"\n"
        outstr += " "*indent + "owner: "+str(self.owner)+"\n"
        outstr += " "*indent + "obj: "+str(self.obj)+"\n"
        # if it's a class, look for classdumps(), otherwise dumps()
        if (inspect.isclass(self.obj)):
            if (hasattr(self.obj,'classdumps')):
                outstr += self.obj.classdumps(indent+1)
        else:
            if (hasattr(self.obj,'dumps')):
                outstr += self.obj.dumps(indent+1)
        return outstr









class MewloRegistryManager(manager.MewloManager):
    """The component registry."""

    def __init__(self, mewlosite, debugmode):
        """Constructor."""
        super(MewloRegistryManager,self).__init__(mewlosite, debugmode)
        # init
        self.components = []
        self.componenthash = {}


    def startup(self, eventlist):
        super(MewloRegistryManager,self).startup(eventlist)


    def shutdown(self):
        super(MewloRegistryManager,self).shutdown()
        #print "** REGISTRY IS SHUTTING DOWN. **"
        self.unregister_all()



    def register_component(self, component):
        """
        Add a component to the registry.
        """
        self.components.append(component)
        # store it in component hash
        id = component.id
        if (id != None and id != ''):
            self.componenthash[id] = component







    def register_class(self, owner, classobj):
        """Proxy for registering a class object, creates a simple component around it."""
        id = self.idfromclassobjectname(classobj.__name__)
        component = MewloComponent(id, owner, {'type':'classwrapper'}, classobj)
        return self.register_component(component)


    def get_class(self, id):
        """Proxy for registering a class object, creates a simple component around it."""
        component = self.getid(self.idfromclassobjectname(id))
        if (component != None):
            return component.obj
        return None


    def idfromclassobjectname(self, objname):
        id = '_classobj:' + objname
        return id




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


    def getid(self, id):
        if (id in self.componenthash):
            return self.componenthash[id]
        return None


    def unregister_byowner(self, owner):
        """Unregister anything owned by the specified ownerobject."""
        self.components= [x for x in self.components if not self.shutdown_obj_ifownedby(x,owner)]

    def shutdown_obj_ifownedby(self, obj, owner):
        """If a component has the owner specified, shut it down and return True; otherwise return False."""
        if (obj.owner != owner):
            return False
        obj.shutdown()
        return True

    def unregister_all(self):
        """Shutdown all registered components."""
        #print "***SHUTTING DOWN REGISTERED COMPONENTS: "+str(len(self.components))
        for component in self.components:
            component.shutdown()
        self.components = []
        self.componenthash = {}



    def dumps(self, indent=0):
        """Debug information."""
        outstr = " "*indent + "Component Registry (" + self.__class__.__name__ + ") reporting in.\n"
        indent += 1
        outstr += " "*indent + "Registered Components: "+str(len(self.components))+"\n"
        for component in self.components:
            outstr+=component.dumps(indent+1)
        return outstr


