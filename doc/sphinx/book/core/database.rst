Mewlo Database / Model System
=============================


We propose to use the SQLAlchemy library to handle all database/orm functionality.
This breaks with our general approach of not using existing 3rd party libraries, but it's one of the few areas where we really don't want to reinvent the wheel.

It would be nice if we could isolate and wrap the SQL Alchemy functionality in our own layer to make it easier to port and swap out SQLAlchemy but I'm not sure that's really feasible.

We can however, list some desires we have for the ORM codebase:

    * A major concern is keeping code and configuration DRY: We don't want to have to repeat field definitions, labels, validation, GUI widget hints, etc.
    * We will want to support database table upgrading when modules are upgraded.
    * We want to support distributed databases, and ability to put different tables on different databases, etc.
    * Good logging and tracking of database operations for performance analysis and debugging.
    * Handle hierarchical class structures well (see Programming Issues to Resolve).



Goals:

	* As little "magic" as possible
	* Use object-oriented interface (Active Record) as much as possible in cases where it won't effect speed
	* But don't try to get too convoluted; when speed is important use lower-level db access.
	* Support multiple databases in same web application (i.e. different models saved to different databases).
	* Built-in support for profiling database access times, and detecting slow/expensive/memory-intensive db calls.
	* Assume we will move mewlo to a non-python language eventually, and code accordingly.
	* Abstract and hide the underlying database engine as much as possible so that db stuff is centralized someplace.
	* We still don't know if we want database engine type we want to use.

Database Engine Thoughts:

	* MongoDb is a nice non-traditional (non-rdbms) nosql oop database, which seems pretty mature and performance focused.
	* MongoDb has a medium-level api interface that we could use directly and would be easy to migrate if we moved languages.
	* SqlAlchemy provides a very nice high-level api for using sql-based database engines.  Very featureful but moving away from python would require complete rewrite.


The Primary Guiding Principle of our Database/Model System is: DRY (Don't Repeat Yourself):

	* There should be one clear place, in code, in the model class, where the complete information for model fields is specified.
	* This specification of fields should completely specify the database table, enough to generate a Create statement for the database, including indices.
	* This specification comprehensive information about how the fields should be presented in user interfaces.
	* This includes validation and display widget information both for gathering these fields on a form (labels, widget types, validation, help hints, etc.).
	* This also included widget hints for presenting admin tabular views of data, searching for it, etc.
	* It should include additional information that will allow us to validate the entire table at any point (e.g. it might specify constraints, etc.)
	* This information should be engine-neutral to the extent possible.



In model classes:
	
	* We have a definedb() function in model classes that defines the database table -- but when should we call it?
	* How do we avoid having to pass around dbmanager reference?
	* How do we divide work between model and manager
	* Can we avoid using any class local data -- since we have an issue with that getting corrupted on module reload
	* Should we divide every model into a Model and a ModelManager, where the ModelManager acts like class static functions, but is basically an instantiated sinlgeton?
	* If we do that, would that make it easier to have drop-in replacements for classes?
	* If we do that, how do we keep track of the ModelManager objects?



Database Model Classes as Tables vs Instantiated Database Model Managers

	* A common approach in frameworks is to have a "Model" class that represents a database table
	* Instantiated objects of this class represent rows/object
	* Static/class functions handle the table-wide functions of finding rows/objects etc.
	* But an alternative is to not use class/static functions of the model class for this purpose.
	* Instead, have two separate classes, one is the Model, and one is the ModelManager
	* The ModelManager would be instantiated and be in charge of table-wide stuff, and of defining the table mappings with the Model object, etc.
	* One advantage of this is that it makes it more natural to think about instantiating multiple copies of a manager, to handle tables that are nearly identical (think about having multiple log file tables).
	* It also seems perhaps cleaner in terms of preserving data for the manager object vs relying on class-based variables.
	* In the case of python, a class is an object, so the differences are much smaller, but I think the principle is valid.