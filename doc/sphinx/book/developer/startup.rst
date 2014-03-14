Component Startup
=================

Startup of mewlo components is not a simple thing, because components have have convoluted inter-dependencies on one another.
These inter-dependencies are further complicated because some components may be created by other components (for example plugins that are instantiated by a pluginmanager component).

We would like to treat all components in a single standard generic fashion with regards to startup.


A new idea for startup of components
------------------------------------

Create a base class for all site components (managers derive from this and are main type of component).

Each component will have 2 functions related to startup (compared to potential 4 now: [prestartup_1, prestartup_2, startup, poststartup]).
The 2 functions will be:
    * def startup_stages_needed():  returns a list of the stagenames that it needs to be called for
    * def startup(stagename): calls startup with a given stagename

We have an ordered list of available stagenames to choose from, things like:
    * "earlycore", "latecore", "premodels", "postmodels", "final"

We will loop through all stages in order in an outer loop.  For each stage, running all components that have said they want to be notified about that stage.

When a new component is added during a stage (which can happen with plugins, mpacks, etc.) it will be immediately run through all stages up to current stage.
Alternatively, mewlo might throw an error or warning when a component added at a latter stage requests notification of an ealier stage, as this could represent a potential problem.
So the logic is, each component should ask to be called on stages where it *NEEDS* to run before the end of that stage, and all components should avoid asking to be notified about a stage that processes before it's creation (e.g. a plugin should not register to be called during "earlycore").

Benefits of this approach over current method:

    * No danger of certain components not receiving startup call for a given stage that they need.
    * Explicit errors when components need a stage that has passed them by.
    * No more proliferation of multiple stage functions.
    * Easier to add additional stages later.
    * Foundation is in place to have more finegrained control over startup order (we could add a weight parameter for example).