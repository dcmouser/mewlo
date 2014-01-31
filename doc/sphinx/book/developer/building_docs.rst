Building Mewlo Documentation
============================

From doc\sphinx run:
	run batch file apidocmake to automatically scan mewlo pack directories and create _apidoc folder with auto found module infos in rst format
	run batch file "make html" to make html version of documentation

Note that the output of documentation is excluded from the git repository.


I have conf.py of sphinx set up to use a couple of extensions:

sphinxcontrib.fulltoc - http://sphinxcontrib-fulltoc.readthedocs.org/en/latest/install.html
 this will do a better job of showing sidebar table of contents.


Modifying Sphinx
----------------

On 9/3/13 I submitted a patch to sphinx to let apidoc output each module documentation on its own page.  In the documentation build batch file (apidocmake.bat), it uses this new apidoc option (--separate-page) to build documentation.
Until it gets accepted, I have included the patched apidoc.py to the doc/notes directory.