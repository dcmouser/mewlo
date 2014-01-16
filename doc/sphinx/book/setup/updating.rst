Updating
========

When mewlo starts up, and periodically, it should do a check for available updates.

When updates are available, they will be visible in the admin control panel.

But updates should be classifiable as being in one of two qualitatively different classes (perhaps using a severity value).

The first class are not-time-sensitive -- the system can run as is, without the updates being applies.
The second class are time-sensitive and critical, and the system should STOP SERVING ALL REQUESTS other than admin access until the upgrade is applied or an override flag is set to bypass this.