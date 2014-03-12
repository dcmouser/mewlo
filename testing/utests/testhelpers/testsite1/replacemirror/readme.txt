This directory mirrors the main mewlo install directory.
In the configuration of the site, we typically instruct mewlo that this directoriy is a potential mirror for the main mewlo/ directory.
This means that on startup, mewlo will scan this directory (and all subdirectories) looking for view (or static) files that will override those under the main mewlo directory.

This is an easy way to replace any built-in view (or static) file in any mewlo core or siteaddon.
