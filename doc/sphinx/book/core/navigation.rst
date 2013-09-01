Navigation Structure and Menu
=============================


Most sites have a hierarchical organizational structure, which some form of menu(s) to help visitors navigate the site, and tell them where they are (via highlighting current page in menu, showing breakcrumbs, etc.).

"Menus" can take the form of horizontal main menus at top of the page, or vertical sidebars.

Mewlo supports a hierarchical site organization model where each node can be annotated with information to support rendering menus, page titles and headings, and breadcrumbs.

In keeping with our consistent approach to Mewlo, and in contrast to other web frameworks, Mewlo implements a single opinionated way of specifying a hierarchical site structure and of keeping track of where the user is in that site structure.

So while different web services may render navigation menus and breadcrumbs differently, Mewlo has one right way of representing these internal data structures -- much as if it was a CMS.


Let's identify the things we want the navigation structure to help us do:

	* Create a hierarchical sidebar/menu of the ENTIRE site structure
	* Highlight the current location (or location path) of the user in such menus.
	* Show breadcrumb trail of where the user is
	* We may want a breadcrumb trail that does not represent the pieces of a hierarchical path but rather a chain of steps
	* We want some branches of the hierarchy to be hidden to people without certain permissions.
	* We want a systematic way to store the hierarchical page navigation data that includes Page Titles, Headings, breadcrumb labels, etc.
	* We want to make it as easy as possible to rearrange page hierarchies.
	* We want addons to be able to create branches of the hierarchy that they manage.
	* When supporting navigation via breadcrumbs or menus/sidebars we sometimes need to do some clever url modifications with parameters

