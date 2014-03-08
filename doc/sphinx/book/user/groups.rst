Group Model
===========


Many frameworks and CMS have "Groups", but a Group in such a system may be as simple as an administrator created collection of Users, with no functionality beyond the fact that it collects users -- typically to categorize for some administrative or ACL

While we will still need such things in Mewlo, for Mewlo, i have in mind Drupal's Organic Groups implementation -- a more robust concept of a GROUP, that may involve groups created by users, with their own pages, sections, content, rules for joining, etc.

In such a scenario, users may APPLY to join a group -- or may be INVITED.  Different groups may have different policies on accepting new users.  Group members may have different rules for choosing who decides which new members can join, etc. And groups may be listed in some kind of directory for people to search and find, etc.

We also probably want to think about a hierarchical organization of Groups -- with or without inherited membership/permissions..

One real dilemma that I have with the Group model is the overlap in functionality between Groups and other "structures" under which we might organize content and users.  Consider the idea of having "Projects" that users can be part of.  Is a Project the same as a Group?  They seem like they would have the same basically functionality and API -- where users could create Projects, join them, have different roles, etc.

So do we want to think of a "Group" as a very abstract container object, from which we can subclass to get "Projects", "User Groups", "Permission Groups", "Newsletter Groups", etc..?



Group Roles
-----------

In Mewlo, group membership is handled via the RBAC permission system.

So, when we say that "User X is in group Z", that is internally represented by a role assignment entry saying that user X has role Y in group Z.

There are multiple role types that relate to group membership, and of course different group roles will have different permissions.