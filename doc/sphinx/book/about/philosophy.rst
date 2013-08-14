Philosophy
==========

It may be valuable to come up with a coherent philosophical approach to design decisions and tradeoffs in Mewlo.  The following reflects my biases:

   * Prefer making maintenance and modification easy over making initial construction fast+easy; do not waste too much time on scaffolding utilities.
   * Be opinionated and enforce conventions that promote readability and predictability over freedom to do things idiosyncratically.
   * Prefer verbose names and code that retains clarity over brevity.
   * Have one clear/true/right way to do something over allowing something to be done in a dozen different ways.
   * Prefer strict behavior and throw clear errors, rather than making default assumptions and trying to be "clever" about what user wants.  When in doubt throw an error, don't try to guess what user wants.
   * Avoid trying to be clever and do things implicitly and automatically.. prefer explicit, transparent, straightforward actions. Avoid default values.
   * MVC (Model-View-Controller) should be the goal in most cases -- but not everything can be cleanly separated as such; prefer OOP over MVC when there is a conflict -- do not force MVC where it's not appropriate.
   * DRY (Don't Repeat Yourself) should be treated as the central dominating principle of design because it so intimately affects maintenance issues.
   * The need to view/search/sort/filter/track and perform-batch-operations on large tabular data (often joined/combined from multiple tables) comes up over and over again -- we want to provide very robust support for such administrative interaction, while avoiding the need to constantly create custom views for different objects, etc.  We want a solution that supports custom administrative views of data when needed, but makes this process as painless as possible.
   * Prefer a generic system of virtual (undoable) deletions, which appears to end-users as if objects were deleted, but with the ability for administrators to undo deletion.
   * Prefer extensions that subclass and add signal handling -- avoid at all costs the need/temptation for users to REPLACE code/classes.
   * A key problem with frameworks/cms is that "add-on" modules break or can be hard to upgrade; this should be a first-class concern in the design of Mewlo -- we need to do everything we can to make upgrading modules easy.
   * Prefer writing a library API and support functions rather than UI front end controllers to do things.
   * Prefer using native code to do configuration and templating, rather than simple config languages, or domain-specific-languages.