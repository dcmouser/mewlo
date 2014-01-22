Mewlo Templating
================


It is common practice in designing web applications to separate the main logic of an application from the textual/html output page contents.

In such cases, one often use some form of "template library" that allows the output page files to contain some minimal logic and variable substitutions, and which facilitates the reuse of common blocks (like headers, footers, sidebars, etc.).



What Template Library Features are Important to Us?
---------------------------------------------------

    * Speed
    * Stability and support by authors
    * Permissive license
    * A clean mewlo-like syntax.
    * Template text files should be able to include each other and use the mewlo "asset/alias" system to locate files.
    * We need to be able to invoke mewlo functions from the template files.
    * We want minimal "magic", and minimal "silent" erroring. 
    * In terms of maintenance and the possibility of moving Mewlo from Python to another language, we might favor a small simple codebase for the template library, at the cost of having to do more support at the Mewlo framework level.
    * We want to be able to easily manage/replace asset files and let users override subsets of them.  This is perhaps the key non-trivial issue that concerns us, and it is discussed in a separate section of the documentation entitled "Asset Files".



Issues to Reolve
-----------------

Should we support multiple template engines and make it easy to choose which one to use?

Our first instinct would be to say yes -- because doing so would be easy from a programming perspective.

But doing so would also violate some of the design principles of Mewlo:

    * There should be one right way of doing things
    * The cost to implement something pales in comparison to the cost of maintaining and supporting it, and the cost that comes with added complications.

These factors argue in favor of having one "official" template library.



Which 3rd Party Template Library to Use?
----------------------------------------

There are many excellent 3rd party template libraries available, and although Mewlo generally avoids using 3rd party components, we have decided that the use of an existing template library makes sense.  It makes sense because the templating library does not have strong effects or dependencies on the rest of the codebase.

Some candiate template libraries include:

    * Jinja2
    * Mako

For now, we have chosen: JINJA2.


