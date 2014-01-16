Coding Style Guidelines
=======================


Consistency and predictability are of criticial importance in this project.


Style:

    * Mewlo code should conform to the official PEP8 style guide -- even though I personally dislike some of the choices it makes.
    * Use docstring documentation for all functions and classes.
    * Be generous with blank lines and comments.


Documentation:

    * We will be using Sphinx to generate documentation from source code
    * See http://docs.python-guide.org/en/latest/writing/documentation.html
    * See http://www.python.org/dev/peps/pep-0257/
    * See http://pythonhosted.org/an_example_pypi_project/sphinx.html#full-code-example
    * See http://matplotlib.org/sampledoc/
    * Sphinx special docstring fields: http://sphinx-doc.org/markup/desc.html
    * See: http://docs.python.org/devguide/documenting.html
    * See: http://datadesk.latimes.com/posts/2012/01/sphinx-on-github/


Naming:

    * Prefer long named functions, properties, classes.
    * Mewlo classes typically have a prefix of M or Mewlo.


File organization:

    * Favor many files arranged hierarchically into subdirectories, as opposed to large files.
    * All of Mewlo code (both core required code and optional 3rd party code) is organized into "packages"; every package should have it's own subdirectory under mewlo/mpackages.
    * The mpackages/core directory is the root to all core Mewlo code.
    * The mpackages/core/helpers directory holds classes and code that have a reasonable likelihood of being generic and usable in non-Mewlo projects.
    * To explain the use of a directory, create a file called "README.txt" and place information there.


File formats:

    * When data files are desired, use .json format files, not xml
    * The extensions of files should match their format -- do not use a custom file extension to indicate purpose; to indicate purpose use a suffix in filename (e.g. "mytest_mpackage.json" uses suffix "_mpackage" to denote it is a package file).


GUI interface:

    * Any GUI or front end pages should be lightweight things that hand off work to back end functions that are not reliant on GUI structures.
    * That is, all code should be organized and structured for non-GUI processing, and should be easily scriptable.
    * All output from functions should not assume that they will be displaying to an interactive screen but may be emailed, logged, etc.


Quotes:

    * See http://stackoverflow.com/questions/56011/single-quotes-vs-double-quotes-in-python
    * Double quotes for text
    * Single quotes for anything that behaves like an identifier (enums, dictionary keys)
    * Double quoted raw string literals for regexps
    * Tripled double quotes for docstrings
    * Another way to think about it -- single quotes for things that you wouldnt want to translate for internationalization, double quotes for things where you would.


Whitespace:

    * Spaces on both sides of assignments and comparisons (around the =, !=, ==), EXCEPT for named function call arguments
    * Space after commas in lists and function args
    * Spaces after the : in dictionary assignment


Multiple variable assignment:

    * Lines which involve multiple variables on the left hand side should be enclosed in () as tuples.  e.g. "(a,b) = func(x)", "for (key, val) in dict.iteritems()"


Formatting strings with arguments:

    * If a text string (specified using double quotes, see above) has arguments in the middle of it, you should use the string format statement to format it: 'there are {0} apples".format(applecount)'.
    * Think of this as being motivated by wanting to run string translation tools on such strings.
    * If the arguments only come at the end of the string, you are free to use string concatenation (+).
    * When creating debug/log type messages in this way, put surround args in single quotes ' for easier identification, e.g. "Could not find object named '{0}'."


Tools:

    * https://pypi.python.org/pypi/flake8
    * https://github.com/jcrocholl/pep8


Python files:

    * All filenames should be in lowercase using underscores to separate words.
    * The top of each code file should look like (leave out import sections that are not used):

            """
            filename.py
            Description of file.
            """ 
            # mewlo imports
            imports of mewlo core files 
            # helper imports
            helper file imports
            # 3rd party lib imports
            3rd party lib imports
            # python imports
            built in python library imports

    * __init__.py files should not have any content; they serve only to mark directories as python traversable packages.