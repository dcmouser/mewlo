This directory holds settings that may contain passwords or other sensitive information, related to a specific host or user.
Because of that, it's important that such files not be committed by accident to a public version control repository.

Any file beginning with "secret_" will be ignored by the version control (git) through the use of the .gitignore file directives.

This may mean that if you download this from a repository, you may need to create your own settings file before you can use this.


