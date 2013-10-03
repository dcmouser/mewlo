Yii
===

Yii is a lean php web framework, similar in spirit to CodeIgniter.
Much of Yii is incredibly intuitive and nicely designed.  It's one of the most enjoyable frameworks I've used.

Things to like about Yii:

    * Forms are handled via yii objects in a nice way.
    * Component classes are named in configuration, so that we can replace any component simply by mapping it to another class
    * The way js and css files are handled indirectly through asset system, and can be automatically minimized, aliased, etc.


Things not to like about Yii:

    * Changing a data model requires manually updating many view files -- very easy to miss updating something, and lots of duplication of code specifying the type of form inputs.
    * To much manual duplication and specification of model property widget types, etc.
    * The automatic traversal of controller paths without having to specify explicit url routes was initially something I loved, but like most "magic" things, I eventually soured on this.  It's too easy for it to get confused, and too easy for things to happen without you understanding what and why.


To look at:

    * Component objects
    * Asset system (private file that can be published publicly)
    * Behaviors