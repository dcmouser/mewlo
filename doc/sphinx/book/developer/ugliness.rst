Ugly Code
=========


8/12/13:
    * We aren't currently using python eggs and officially installable packages for different components


8/13/13:
    * It looks like when dynamically importing modules (ie packages), relative imports are not being supported; this could create hardships.
    * See http://stackoverflow.com/questions/5078590/dynamic-imports-relative-imports-in-python-3
    * I solved this for now by using version3 of the import function in callables.py


8/13/13:
    * We are still throwing some exceptions in mcontroller and helpers/callables modules.


8/15/13:
    * We sometimes use ' and sometimes use " for strings; decide on a standard and explain why and make all consistent.
    * We sometimes use % operator, and sometimes use +; be consistent.  Is % being deprecated?


8/15/13:
    * The event creation shortcut functions (see bottom of event.py) should use args,kargs to be simpler.


8/15/13:
    * We need to put in place something to check for python3 compatibility.


8/15/13:
    * Our debug functions are ugly -- especially the indentstr parts.