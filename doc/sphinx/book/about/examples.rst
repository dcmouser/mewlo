Examples
========


In order to better understand how mewlo fits into the existing ecosystem of web and CMS frameworks, it may be useful to look at some examples of how certain things are handled by Mewlo.


Site navigation hierarchy and menus
-----------------------------------

In a CMS (like Drupal for example), there typically exists a robust user GUI that can be used by administrators to create a hierarchical site navigation menu or navigation bar.  Such a facility may begin as a simple feature, but soon turns into an elaborate system that can handle scenarios where certain areas are shown to certain people, certain pages and links have dynamic labels, etc.

For web frameworks -- the issue of hierarchical site navigation structure and site menus/navigation bars is almost always outside the scope of the framework.  It may be argued that a minimal web project may not need such a thing -- though most will.  But building such a system is typically left for the coder working with the framework.

Mewlo takes a middle ground.  It includes in its core a powerful and robust system for dealing with site navigation, menus, breadcrumbs, etc.  But there is no interactive friendly GUI for moderators and administrators.  As with most of Mewlo -- it is designed to be configured, customized, and extended by the developer working on a particular mewlo-powered web site.


