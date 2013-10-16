Installation
============

Updated 7/27/13



STEP 1 - Create virtual environment for Mewlo development
---------------------------------------------------------

You want to isolate your install of mewlo, to test in a prestine environment

Create a virtualenv to isolate mewlo development, eg:
  On windows:
  ..\Scripts\virtualenv --no-site-packages mewloenv

Create simple batch file to setup virtual environment in commandline:
  On windows:
  start C:\Langs\Python2\venv\mewloenv\Scripts\activate.bat



STEP 2 - Adding Mewlo directory to python path
----------------------------------------------

You need to add the top mewlo directory to your python path so it can be found when you execute a command like "import mewlo.mpackages"
One way is to add the path to it to site-packages\easy-install.pth



STEP 3 - Install required helper packages
-----------------------------------------

Install the Werkzeug package which is temporarily being used to do some lower-level request+response work:
  pip install Werkzeug


Install the jinja2 template package which is used for template output
  pip install jinja2



To build documentation:
	pip install Sphinx
	pip install rst2pdf <--- this fails in my (ms windows-based) virtualenv



STEP 4 - Testing
----------------

After activating the virtualenvironment (using batch file or whatever),
go into the testing/utests directory and run:
	python utest1.py
or:
	python demosite1.py




