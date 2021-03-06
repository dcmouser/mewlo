Documentation Style
===================


Code maintenance has top priority on this project, and consistency is highly valued.

    * We will be using an automated source code scanning tool to generate documentation dynamically.
    * We are currently using Sphinx for this.
    * This means that the source code itself IS the primary means of documenting the system.
    * As such, it should be complete and verbose.



All functions accept simple accessors and constructors should use docstring comments.  All classes should have lengthy docstring comments.

One line docstring comments can go all on one line as a sentence ending with a period, e.g.
    * """This is a one line comment."""

Multi-line docstring comments should have the """ on lines alone, e.g.:

				"""
				This is a multiline docstring comment.
				With multiple lines.
				"""



Whitespace is encouraged.  Use multiple blank lines to separate functions and classes.



We will be using Sphinx to generate documentation from source code
    * See http://docs.python-guide.org/en/latest/writing/documentation.html
    * See http://www.python.org/dev/peps/pep-0257/
    * See http://pythonhosted.org/an_example_pypi_project/sphinx.html#full-code-example
    * See http://matplotlib.org/sampledoc/
    * Sphinx special docstring fields: http://sphinx-doc.org/markup/desc.html
    * See: http://docs.python.org/devguide/documenting.html
    * See: http://datadesk.latimes.com/posts/2012/01/sphinx-on-github/
