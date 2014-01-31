Mewlo Views
===========

View files are template files, served up as html or whatever, by controllers in response to requests.

The [templates] documentation page goes into details about template file formats, rendering, variables, etc.

This document discusses Views before the template rendering step.

In general, loading and displaying View files is a straightforward process.  Here's a sample call from a controller function to render a view:

    response.render_from_template_file('${siteviewpath}/home.jn2')

The '${siteviewpath}' alias replacement points to a view directory in the custom site.

Things get complicated when we have core or addon packs which want to provide view files that the user *might* want to replace, or which might be replaced by theme packs.

See the [themes] document for information on handling theme overrides.