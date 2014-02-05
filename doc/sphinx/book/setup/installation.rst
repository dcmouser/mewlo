Installation
============

Updated 7/27/13


STEP 0 - Install Python and PIP
---------------------------------------------------------

1.Install python 2.7 (not 3.x)

2. For windows, you need to install pip:



STEP 1 - Create virtual environment for Mewlo development
---------------------------------------------------------

Install virtualenv:
	pip install virtualenv

You want to isolate your install of mewlo, to test in a pristine environment

Create a virtualenv to isolate mewlo development, eg:
  On windows:
  ..\Scripts\virtualenv --no-site-packages mewloenv

Create simple batch file to setup virtual environment in commandline:
  On windows:
  start C:\Langs\Python27\venv\mewloenv\Scripts\activate.bat



STEP 2 - Adding Mewlo directory to python path
----------------------------------------------

You need to add the top mewlo directory to your python path so it can be found when you execute a command like "import mewlo.mpacks"
One way is to add the path to it to a pth file in site-packages\
for example make a file called site-packages\myextra_sitepackages.pth
whose contents is:
e:\websitehttp\mewlo







STEP 3 - Install required helper packages
-----------------------------------------

Install the Werkzeug package which is temporarily being used to do some lower-level request+response work:
  pip install Werkzeug

Install the jinja2 template package which is used for template output
  pip install jinja2

Install the SqlAlchemy module used for form processing
  pip install sqlalchemy

Install the Requests module used for web downloading
  pip install requests

Install the WTForms module used for form processing
  pip install wtforms

Experimenting with pyzmail:
  pip install pyzmail


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




