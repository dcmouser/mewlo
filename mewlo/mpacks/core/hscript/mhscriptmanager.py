"""
mhscriptmanager.py
helper object for html/jss/css script that can get included on pages
"""


# mewlo imports
from ..manager import manager
from ..setting.msettings import MewloSettings
from ..eventlog.mevent import EFailure, EException
from ..constants.mconstants import MewloConstants as mconst
from ..helpers import misc
from ..asset import massetmanager









class MewloHScript(object):
    """Subclasses of this represent different javascript and css libraries.
    By default we make it very easy to create a new simple hscript class and use it, but if needed an hscript object can overide any of these functions for more advanced use.
    ATTN:TO - add some version # suppport.
    """

    # all hscript aliases and assets are treated as being under a mnamespace
    DEF_hscript_mnamespace = 'hs'

    def __init__(self, idname_override=None):
        self.idname_override = idname_override
        self.hscriptmanager = None

    def get_idname(self):
        """Accessor that allows override."""
        if (self.idname_override):
            return self.idname_overide
        return self.idname_default

    def calc_asset_varrep(self, varname):
        """Simple wrapper to redirect to assetmanager calc_asset_varrep."""
        idname = self.get_idname()
        assetmanager = self.hscriptmanager.sitecomp_assetmanager()
        mnamespace = self.DEF_hscript_mnamespace
        return assetmanager.calc_asset_varrep_withmnamespace(mnamespace, idname, varname)


    def get_mewlosite(self):
        return self.hscriptmanager.mewlosite

    def startup_register(self, hscriptmanager):
        """Store hscriptmanager (we can get mewlosite through it."""
        self.hscriptmanager = hscriptmanager
        # make assets for the library available
        asset_filepath = getattr(self, 'asset_filepath', None)
        if (asset_filepath):
            self.add_script_assetfilepath(asset_filepath)
        # sometimes we may have asset files we need to alias but which will have been exposed by another required script, so we don't need to recopy or expose under a dif name, so we alias from the other
        same_asset_filepath_as_hscript = getattr(self, 'same_asset_filepath_as_hscript', None)
        if (same_asset_filepath_as_hscript):
            self.clone_aliases_from_another_hscript(same_asset_filepath_as_hscript)


    def make_liburl(self, src, request, is_relative):
        """Make a lib url, relative or absolute."""
        if (misc.isabsoluteurl(src)):
            # it's already absolute, just return it
            return src
        if (is_relative):
            src = self.calc_asset_varrep('urlrel')+'/'+src
        else:
            src = self.calc_asset_varrep('urlabs')+'/'+src
        # ATTN:TODO resolve it - we should resolve these at startup and not on every request
        src = request.resolve(src)
        # return it
        return src

    def add_script_assetfilepath(self, asset_filepath):
        """Add a script's filepath."""
        # add asset
        idname = self.get_idname()
        assetmanager = self.hscriptmanager.sitecomp_assetmanager()
        mountid = 'internal_assets'
        assetmanager.add_assetsource( massetmanager.MewloAssetSource(id=idname, mountid=mountid, filepath=asset_filepath, mnamespace=self.DEF_hscript_mnamespace) )


    def addtohead(self, request , is_relative=True):
        """Default subclass function; this does the actions needed to register the script for the page so it loads the js and css it needs."""

        # first do any recursive REQUIRED includes
        requires = getattr(self, 'requires', [])
        for requiredlibname in requires:
            self.hscriptmanager.hscript(requiredlibname).addtohead(request, is_relative)

        # add any comment?
        comment = getattr(self,'comment', None)
        if (comment):
            request.response.add_headitem_comment(comment, is_unique=True)

        # add the head items js src includes
        js_src = getattr(self,'js_src', [])
        for src in js_src:
            src = self.make_liburl(src, request, is_relative)
            request.response.add_headitem_js({'src':src})

        # add the head items js script inner includes (raw js code in header)
        js_inner = getattr(self,'js_inner', [])
        for inner in js_inner:
            request.response.add_headitem_js({'_inner':inner})

        # any helper css files?
        css = getattr(self,'css', [])
        for src in css:
            src = self.make_liburl(src, request, is_relative)
            request.response.add_headitem_css({'href':src})



    def clone_aliases_from_another_hscript(self, source_idname):
        """Clone aliases from one to another."""
        assetmanager = self.hscriptmanager.sitecomp_assetmanager()
        assetmanager.redirect_asset_aliase_set(self.DEF_hscript_mnamespace, self.get_idname(), self.DEF_hscript_mnamespace, source_idname)



    def calc_filepath(self, request, subdir, fname):
        """Calculate the local template file path."""
        src = self.calc_asset_varrep('filepath')
        if (subdir):
            src+='/'+subdir
        if (fname):
            src+='/'+fname
        # ATTN:TODO resolve it - we should resolve these at startup and not on every request
        src = request.resolve(src)
        # return it
        return src












































class MewloHScript_JQuery(MewloHScript):
    """JQuery js library."""
    idname_default = 'jquery'
    comment = 'jquery javascript library (http://jquery.com)'
    js_src = ['jquery-2.1.0.js']
    asset_filepath = misc.calc_modulefiledirpath(__file__, 'jquery/assets')


class MewloHScript_JQueryCdn(MewloHScript):
    """JQuery js library."""
    idname_default = 'jquery_cdn'
    comment = 'jquery javascript library (http://jquery.com)'
    js_src = ['http://www.google.com/jsapi']
    js_inner = ['google.load("jquery","1.4")']


class MewloHScript_Angular(MewloHScript):
    """Angular js library."""
    idname_default = 'angular'
    comment = 'angular javascript library (http://angularjs.org)'
    js_src = ['angular.js']
    asset_filepath = misc.calc_modulefiledirpath(__file__ , 'angular/assets')


class MewloHScript_Bootstrap(MewloHScript):
    """bootstrap css library."""
    idname_default = 'bootstrap'
    comment = 'bootstrap css library (http://getbootstrap.com)'
    js_src = ['//netdna.bootstrapcdn.com/bootstrap/3.1.1/js/bootstrap.min.js']
    css = ['//netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap.min.css', '//netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap-theme.min.css']


class MewloHScript_Pure(MewloHScript):
    """pure css library"""
    idname_default = 'pure'
    comment = 'pure css library (http://purecss.io)'
    css = ['http://yui.yahooapis.com/pure/0.5.0-rc-1/pure-min.css']


class MewloHScript_Foundation(MewloHScript):
    """foundation css library"""
    idname_default = 'foundation'
    comment = 'foundation css library (http://foundation.zurb.com)'
    js_src = ['js/foundation.min.js']
    css = ['css/normalize.css', 'css/foundation.css']
    asset_filepath = misc.calc_modulefiledirpath(__file__ , 'foundation/assets')


































class MewloHScript_JQuery_ImageBrowser(MewloHScript):
    """JQuery addon."""
    idname_default = 'jquery_imagebrowser'
    requires = ['jquery']
    comment = 'jquery - jquery_imagebrowser (homemade addon for jquery by mouser@donationcoder.com, 2011)'
    js_src = ['libs/imagebrowser/imagebrowser.js', 'libs/imagebrowser/jquery.scrollTo-min.js']
    css = ['libs/imagebrowser/imagebrowser.css']
    same_asset_filepath_as_hscript = 'jquery'
    #
    viewdir = 'libs/imagebrowser/_views'
    viewfiles = {
        'widget_main': 'widget_main.jn2',
        'widget_js': 'widget_js.jn2',
        }


    def embed(self, request, imagebrowser_ajax_url='', imageroot='', idsuffix=''):
        """Embed on page."""

        # ATTN: we are now using a late-loading system of page header stuff to let the widget on the page do it's own addtohead stuff;
        # normally we would have to call addtohead BEFORE the template was rendering, but if the user writes the template tag to include page headers using a late-resolving method (see header.jn2), we can do this here
        # note that because we automatically ignore duplicate addtohead stuff, it is safe to call in both places
        self.hscriptmanager.hscript('jquery_imagebrowser').addtohead(request)

        # get the sections from template files
        argdict = {
            'imagebrowser_ajax_url': imagebrowser_ajax_url,
            'divid_imagebrowser': 'div_imagebrowser'+idsuffix,
            'divid_directorypanel': 'div_directorypanel'+idsuffix,
            'divid_filepanel': 'div_filepanel'+idsuffix,
            'fieldid_fileinput': 'field_fileinput'+idsuffix,
            # imageroot should be '' or '/path/to/start'
            'imageroot': imageroot,
        }
        #
        templatefilepath = self.calc_filepath(request, self.viewdir, self.viewfiles['widget_main'])
        widget_main_html = self.get_mewlosite().renderstr_from_template_file(request, templatefilepath, argdict)
        #
        templatefilepath = self.calc_filepath(request, self.viewdir, self.viewfiles['widget_js'])
        widget_js_html = self.get_mewlosite().renderstr_from_template_file(request, templatefilepath, argdict)

        # build html
        reth = widget_main_html + widget_js_html

        return reth































































class MewloHScriptManager(manager.MewloManager):
    """Manages MewloHScript objects."""

    # class constants
    description = "Manages javascript, css, and other html framework libraries for use on pages."
    typestr = "core"



    def __init__(self, mewlosite, debugmode):
        """Constructor."""
        super(MewloHScriptManager,self).__init__(mewlosite, debugmode)
        #
        self.needs_startupstages([mconst.DEF_STARTUPSTAGE_preassetstuff])
        self.hscripts = {}



    def startup_prep(self, stageid, eventlist):
        """
        This is invoked by site strtup, for each stage specified in startup_stages_needed() above.
        """
        super(MewloHScriptManager,self).startup_prep(stageid, eventlist)
        if (stageid == mconst.DEF_STARTUPSTAGE_preassetstuff):
            self.register_hscripts()




    def register_hscripts(self):
        """Register javascript libraries internally for later lookup."""
        # ATTN:TODO - later we can move these into independent mpacks that register themselves
        self.register_hscript(MewloHScript_JQuery())
        self.register_hscript(MewloHScript_Angular())
        self.register_hscript(MewloHScript_Bootstrap())
        self.register_hscript(MewloHScript_Pure())
        self.register_hscript(MewloHScript_Foundation())
        self.register_hscript(MewloHScript_JQuery_ImageBrowser())



    def register_hscript(self, hscript):
        """Register javascript libraries internally for later lookup."""
        idname = hscript.get_idname()
        # store it
        self.hscripts[idname] = hscript
        # let it do any startup stuff
        hscript.startup_register(self)



    def hscript(self, idname):
        """Standard accessor."""
        return self.hscripts[idname]
























