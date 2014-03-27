File Uploads
============

There are many places where we may want to allow a user to upload files.

Some examples:
    * Uploaded a custom avatar (image)
    * Uploaded attachments to a forum post (multiple attachments per post, of arbitrary file types).

There are 3 aspects we are concerned with:
    * Performing the actual upload and storage of the file; this involves giving it a unique name, deciding where to place it, and performing any operations on it at storage time (thumbnailing, etc.).
    * Using the uploaded file -- that is, allowing the right people to view it, getting a list of uploaded files matching a certain type, on-the-fly thumbnailing, user-deletion of uploaded files, etc.
    * Back-end administration; that is, allowing administrators to search and manage uploaded files, find broken files, delete old files, etc.

Some issues to consider:
    * Sometime we will want to store (expose) a file in a directory served by a traditional web server for fast serving of static files (for example for avatar images).
    * While other files we will want to protect and internally serve only after checking permissions.
    * Even though it makes little difference when managing files from within mewlo, we would like files to be stored in nicely nested subdirectories for easier external management and backup (ie year/month/day)

