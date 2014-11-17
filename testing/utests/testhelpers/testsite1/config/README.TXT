This directory holds settings that may contain passwords or other sensitive information, related to a specific host or user.
Because of that, it's important that such files not be committed by accident to a public version control repository.

Any file beginning with "secret_" will be ignored by the version control (git) through the use of the .gitignore file directives
(assuming the .gitignore file is in this directory).

If you use another version control system you should ensure that secret_* files are never committed/shared.

---

Because secret_* files are not distributed, you may need to create your own secret_* settings file(s) before you can use a freshly checked out repository.

---


So, for example, after grabbing mewlo from version control, make a file called mouser_secret.py in this directory, whose contents are:

mail_smtp_host = 'smtp.comcast.net'
mail_smtp_login = 'x@comcast.net'
mail_smtp_port = 465
mail_smtp_mode = 'ssl'
mail_smtp_password = 'xxxx'
mail_from = 'x@comcast.net'

And change those values to point to a valid smtp account you own.

Until you do that, mewlo will not be able to send out emails.

---

Note: You can easily switch between multiple configuration files to use at the commandline when starting a mewlo server.
This is designed to let you keep different server configurations in one place and switch between them easily.
