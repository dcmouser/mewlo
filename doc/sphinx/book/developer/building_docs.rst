Building Mewlo Documentation
============================

From doc\sphinx run:
	run batch file apidocmake to automatically scan mewlo package directories and create _apidoc folder with auto found module infos in rst format
	run batch file "make html" to make html version of documentation

Note that the output of documentation is excluded from the git repository.


I have conf.py of sphinx set up to use a couple of extensions:

sphinxcontrib.fulltoc - http://sphinxcontrib-fulltoc.readthedocs.org/en/latest/install.html
 this will do a better job of showing sidebar table of contents.
