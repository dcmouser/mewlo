Naming Style
============


This section will describe the guidelines for naming classes, functions, variables, and database fields.



Model Database Fields
---------------------

When a database model field is storing a serialized string representing a dictionary (or object, but dictionary is preferred), the name of this database field should be "WHATEVER_serialized".
Date/timestamp fields should always start "date_"
Every database model(table) should have a primary id field.
