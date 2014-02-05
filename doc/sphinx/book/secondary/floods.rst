Flood Detector
==============


There are lots of cases where we need to detect when there is a flood of events of a certain type, and take certain actions when they happen.

For example, if a single ip is hammering random login or verification attempts, we want to ban them.
If errors which require sending an email to an admin are triggered in some way that they create a flood of emails we want to stop.