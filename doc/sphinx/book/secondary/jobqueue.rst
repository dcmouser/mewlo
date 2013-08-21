Job Queue
=========


There are times when we will want to queue up jobs to be performed when appropriate.  This is different from a cron system (though a cron system may invoke the Job Queue system regularly).

The Job Queue system is more appropriate for when users request some action (like a report or export) that could take up significant cpu if many people requested such things at the same time.  So the Job Queue would basically queue up the jobs to be performed when load is low, with result mailed to user when complete.