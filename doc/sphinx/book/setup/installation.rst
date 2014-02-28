Installation
============

Updated 02/27/2014



STEP 0a - System preparation - Installing Python with PIP
---------------------------------------------------------

1.Install python 2.7
	* Python Installer: http://www.python.org/downloads/

2. For windows, you need to install pip using the get-pip.py script.
	* Get-pip.py: http://www.pip-installer.org/en/latest/installing.html


STEP 0b - Checkout the mewlo repository from GIT
------------------------------------------------

1. It is recommended that a Git client be utilized with this project. The project is hosted at the GitHub URL below, and 
	tools like SmartGit, or the GitHub desktop client can help synchronize code changes between developers. 
	
	* SmartGit: http://www.syntevo.com/smartgithg/
	* GitHub Desktop: http://windows.github.com/

2. Mewlo GIT repository is at https://github.com/dcmouser/mewlo




STEP 1 - Create the Mewlo virtual environment 
---------------------------------------------

* Install virtualenv:
	
	Via the command line, browse to your python path. Change to the scripts folder and run the following command:
	
	**pip install virtualenv**

* Setup the Mewlo Virtual Environment
	
	* Create the virtual environment by invoking the virtualenv command:
	
		* C:\coding\python\scripts\virtualenv.exe --no-site-packages mewloenv
		
		** NOTE: Replace the "C:\coding" folder with your python path **
		
	* Setup a batch file (Windows) to launch the mewlo development environment

		* In a blank text file, insert the following command
			* start "c:\coding\python27\scripts\mewloenv\scripts\activate.bat"
		
		* Save the file as mewlo.bat and place it wherever you need it for rapid access

STEP 2 - Adding Mewlo directory to python path
----------------------------------------------

The next step in the process is to setup python to recognize where the top-level folder for Mewlo resides. This will come
in handy when you execute commands like "import mewlo.mpacks". 

	* Create a blank file in the C:\Coding\Python27\scripts\virtualenv\mewloenv\scripts\ folder named myextra_sitepackages.pth
	* Inside of this file, add the path to your mewlo source: e.g., C:\Coding\Mewlo

STEP 3 - Setup the Mewlo Environment
------------------------------------

** IMPORTANT NOTE: Before proceeding, invoke a mewlo shell by executing your mewlo.bat file created above **

	* Change your path to the scripts folder in your mewlo virtual environment (e.g., c:\coding\python27\scripts\mewloenv\scripts\)
	
	1. Install the Werkzeug request-response framework: **pip.exe install Werkzeug**
	2. Install the Jinja2 templating package: **pip.exe install jinja2**
	3. Install the SQLAlchemy form processing module: **pip.exe install sqlalchemy**
	4. Install the requests web downloading module: **pip.exe install requests**
	5. Install the WTForms forms processing module: **pip.exe install wtforms**
	6. Install the PYZMail email module: **pip.exe install pyzmail**
	7. Install the required sphinx restructured text (rst) documentation generation tools:
		a. Core modules: **pip.exe install sphinx**
		b. Contributor modules: **pip.exe install sphinxcontrib-fulltoc**
	8. Install the restructured text to PDF conversion module: **pip.exe install rst2pdf**

STEP 4 - Launching the Mewlo Web Server Process
-----------------------------------------------

** NOTE: This step requires you to remain inside of your mewlo virtual environment shell**

	* Validate the installation by executing the following command from  the testing\utests folder:
		* python utest.py
		
		* You should receive a note stating two tests completed successfully.
		* **NOTE: Ignore any warnings about LogManager**
		
	* Launch the python embedded web server to test out Mewlo
		* Change to the mewlo\testing\utests\testhelpers\testsite1 folder
		* Launch the server process by executing: python testsite1.py --runserver
		
		* Once you received a message stating that the web server is starting, you can access Mewlo by browsing to: 
			* http://127.0.0.1:8080
