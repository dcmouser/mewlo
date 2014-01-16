This directory provides tests for the mewlo system code.

This code is not called by a normal mewlo system but would be run from outside of it.

//---------------------------------------------------------------------------




//---------------------------------------------------------------------------
We can run unit tests, on the site defined in testsite1/:
UNIT TEST demos, run:

python utest1.py
//---------------------------------------------------------------------------





//---------------------------------------------------------------------------
We can also run the same demo site in  testsite1/ directly (not via unit tests),
 and have it parse commandline for various options/tests:

E:\WebsiteHttp\mewlo\testing\utests>python demosite1test.py --help

and to run the server to serve pages

E:\WebsiteHttp\mewlo\testing\utests>python demosite1test.py --runserver
//---------------------------------------------------------------------------