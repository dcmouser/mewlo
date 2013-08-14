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
  On windows:
  pip install Werkzeug

To build documentation:
	pip install Sphinx
	pip install rst2pdf <--- this fails in my virtualenv



STEP 4 - Testing
----------------

After activating the virtualenvironment (using batch file or whatever),
go into the demosites/test1 directory and run:
	python testsite1.py

This will run the testsite1.py script, which defines a test website with some test routes.
Running it should first display some debug information, and then start a webserver on your localhost at port 8080
To test, open up your web browser and point to:
  http://127.0.0.1:8080/test/hello/name/mouser


