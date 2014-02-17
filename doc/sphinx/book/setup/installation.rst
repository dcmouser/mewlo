Installation
============

Updated 7/27/13



STEP 0a - Install Python and PIP
---------------------------------------------------------

1.Install python 2.7 (not 3.x)

2. For windows, you need to install pip:

    See: http://dabapps.com/blog/introduction-to-pip-and-virtualenv-python/
    and: http://www.pythonforbeginners.com/basics/how-to-use-python-virtualenv
    and: http://stackoverflow.com/questions/17737203/python-and-virtualenv-on-windows



STEP 0b - Checkout the mewlo repository from GIT
---------------------------------------------------------

1. I use SmartGit on windows
http://www.syntevo.com/smartgithg/

2. Mewlo GIT repository is at https://github.com/dcmouser/mewlo




STEP 1 - Create virtual environment for Mewlo development
---------------------------------------------------------

Install virtualenv:
	pip install virtualenv

You want to isolate your install of mewlo, to test in a pristine environment

Create a virtualenv to isolate mewlo development, eg:
  On windows:
  ../Scripts/virtualenv --no-site-packages mewloenv

Create simple batch file to setup virtual environment in commandline:
  On windows:
  start C:/Langs/Python27/venv/mewloenv/Scripts/activate.bat



STEP 2 - Adding Mewlo directory to python path
----------------------------------------------

You need to add the top mewlo directory to your python path so it can be found when you execute a command like "import mewlo.mpacks"
One way is to add the path to it to a pth file in the mewlo virtualenv site-packages/ directory
for example make a file called ./venv/mewloenv/Lib/site-packages/myextra_sitepackages.pth
whose contents is:
e:/websitehttp/mewlo

(assuming that e:/websitehttp/mewlo is your top level mewlo directory, the one with the readme.md in it and doc subdirectory)






STEP 3 - Install required helper packages
-----------------------------------------

!!!!!!!!!IMPORTANT!!!!!!!!!
YOU NEED TO BE ACTIVATED IN YOUR MEWLO VIRTUAL ENVIRONMENT (use the activate.bat on windows) WHEN YOU INSTALL THE BELOW PACKAGES
!!!!!!!!!IMPORTANT!!!!!!!!!


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


To build documentation (optional and may require some batch files to assist):
	pip install Sphinx
  pip install sphinxcontrib-fulltoc
  
  PDF output is broken and not working but if working you would:
	pip install rst2pdf





STEP 4 - Testing
----------------

!!!!!!!!!IMPORTANT!!!!!!!!!
YOU NEED TO BE ACTIVATED IN YOUR MEWLO VIRTUAL ENVIRONMENT (use the activate.bat on windows) WHEN YOU TRY THIS STUFF
!!!!!!!!!IMPORTANT!!!!!!!!!

After activating the virtualenvironment (using batch file or whatever),
go into the testing/utests directory and run:
	python utest1.py





