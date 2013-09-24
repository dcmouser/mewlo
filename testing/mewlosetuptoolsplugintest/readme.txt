This directory is used to test setuptools based plugin auto discovery via entry points.

That is why it is purposefully outside of the normal autodiscovery plugin directories used by mewlo.

The idea is that when this EGG is loaded into python, it will be discoverable as a plugin via Mewlo.

Note that we only use the setuptools provided entrypoint functionality as a way of letting users install
a mewlo plugin using setuptools system as a standard site-package outside of mewlo directory, and as a
way of helping mewlo discovery these external plugin files.  After that, the plugin/extension files are
processed identically to how they are when discovered inside the mewlo extension directory.

See the setup.py file for more information.




For more info see: http://bashelton.com/2009/04/setuptools-tutorial/#advanced_options-entry_points





To build the egg from this, change to root directory of package (where setup.py lives), and run:

$ python setup.py bdist_egg

Then to install into your site packages:

$ python setup.py install


IMPORTANT: MAKE SURE YOU RUN THIS FROM YOUR VIRTUAL ENVIRONMENT!



Then when you run Mewlo, it should "discover" the installed addon package.




To manually install for development mode,
go to virtual environment site-packages directory and make file "mewlotestplug.egg-link"
with contents like "E:\WebsiteHttp\mewlotestplug"
and edit site-packages\easy-install.pth to add a line saying same thing "E:\WebsiteHttp\mewlotestplug"

NOTE: I could not get this to work when inside of the mewlo package, only when outside

