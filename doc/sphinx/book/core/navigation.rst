Navigation Structure and Menu
=============================


Most sites have a hierarchical organizational structure, which some form of menu(s) to help visitors navigate the site, and tell them where they are (via highlighting current page on a navigation bar, showing breadcrumbs, or some combination of such things).  Menus can take the form of horizontal main menus at top of the page, or vertical sidebars.  Sometimes they are deep interactive javascript things that let users go anywhere on site; sometimes they just give the user access to the major site areas.

Mewlo provides a system, called NavNodes, whose purpose is to assist in producing these kinds of navigational tools and keeping track of the user's location on the site.

In keeping with our consistent approach to Mewlo, and in contrast to other web frameworks, The NavNode system is opinionated in how it requires the site structure to be specified.  Mewlo has one right way of representing these internal data structures -- much as if it was a CMS.

Here are the kinds of things we want a coder to be able to do with this system:

	* Create a hierarchical sidebar/menu of the ENTIRE site structure
	* Highlight the current location (or location path) of the user in such menus.
	* Show breadcrumb trail of where the user is
	* We may want a breadcrumb trail that does not represent the pieces of a hierarchical path but rather a chain of steps
	* We want some branches of the hierarchy to be hidden to people without certain permissions.
	* We want a systematic way to store the hierarchical page navigation data that includes Page Titles, Headings, breadcrumb labels, etc.
	* We want to make it as easy as possible to rearrange page hierarchies.
	* We want addons to be able to create branches of the hierarchy that they manage.
	* When supporting navigation via breadcrumbs or menus/sidebars we sometimes need to do some clever url modifications with parameters


Some more details of the NavNode implementation:

A site has a kind of "implicit" hierarchy defined by the urls it responds to.  Such urls are defined by the "Route" system.  Often the definition of routes has a kind of hierarchical feel.  But routes (urls) themselves are not explicitly hierarchically arranged.  Routes are not explicitly related to one another.

The NavNode system is an explicit graph of site "pages" (nodes).  While routes correspond to the input side of the system, NavNodes correspond to the output side of the system.  We might think of each Route as a way into the system, and each NavNode as a possible page output.

Frequently, a single Route input will map to a single NavNode output, but not always.

NavNodes are arranged in a graph of parents and children. This graph is built at runtime using id names to refer to parents and children.  In this way it is easy to merge different parts of the graph from extensions and addons and splice in NavNodes.

At a minimum, a NavNode simply consists of a unique id name and a list of parents and/or children.  It can also be adorned by arbitrary properties.  These properties can be used to specify page titles, menu titles, mouseover hints, and arbitrary data.

A NavNodeManager class is used to build structures from the NavNode graph that can be used for creating site menus, breadcrumbs, etc.

We can think of the construction of such site menus/sidebars/breadcrumbs as taking place at 3 levels:

  * The first level is the raw collection of NavNodes which represent the unchanging totality of the site structure.
  * At the second level is a datastructure of NavNodes (a hierarchy or list) constructed for a particular user visit, with annotations on the node indicating the active path, with some nodes hidden or disabled, and with textual properties replaced based on the context.
  * At the third level this datastructure is rendered into html/javascript for display; there may be many ways to customize this.


An example:

Consider a simple site with a 2-level deep hierarchy.  On the first level we have the main pages for "Home", "About", "Help".
Under "Help" we have our 2nd level of the hierarchy with pages for "Help with the Site" and "Help signing up".

Additionally, we have 3 more links we want to show at the top level, but they won't always be visible.  These links are "Login", "Logout (USERNAME)", "Register".  It is these 3 links(pages) that require special handling.

We specify the NavNode site structure, adding our 3 special NavNodes where we would want them shown.  But for these 3 special nodes, we will specify a custom function for their flag_visible property.  This function will be passed the NavNode in question, along with the "page context" that is provided when the output page is created.  Furthermore, the title text for the "Logout" NavNode will be generated either from a custom function we write, or using simple replacement template based again on the "page context".

When generating the output for a page, here's how the controller/view indicates the NavNode representing the current page and specifies the page context.  From within code it would look like:

  * response.setpage('Help',pagecontext)

Where the first parameter is the idname of the NavNode representing this output page, and pagecontext is a dictionary of data to make available to the NavNodes for custom functions and template replacements.  Typically it would consist of the User class for any logged in user, but could include any additional information that might be useful for the navigation structures (menus, breadcrumbs, etc.).

Note that this functional call does not actually render any output.  One still has to call a function to render a template to the display (or otherwise generate output).  It is from this template that the menu/breadcrumb/etc rendering would actually take place.  The setpage() function is simply a way of setting information about the output page to be rendered.
