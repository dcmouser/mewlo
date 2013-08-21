Read Tracking
=============


A site often wants to help users track what content they have read and what content is new to them.
This has to be done efficiently and cleverly in order to avoid exploding memory requirements.

For a forum this often amounts to keeping track of the last post read in each thread by each user, but also allowing users to say "mark all messages (in this section) as read", and storing that fact compactly (e.g. simply storing the fact that all messages in section X below ID #X are considered as read).

More complex schemes would also be possible such as storing intervals of read content Ids, or automatically simplifying the list of content read by a user when it gets very old.