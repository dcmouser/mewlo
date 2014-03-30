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
    """Subclasses of this represent different javascript and css libraries."""

    def __init__(self, idname_override=None):
        self.idname_override = idname_override

    def startup_register(self, hscriptmanager):
        """Store hscriptmanager (we can get mewlosite through it."""
        self.hscriptmanager = hscriptmanager
        # make assets for the library available
        asset_filepath = getattr(self, 'asset_filepath', None)
        if (asset_filepath):
            self.add_script_assetfilepath(self.get_idname(), asset_filepath)

    def get_idname(self):
        """Accessor that allows override."""
        if (self.idname_override):
            return self.idname_overide
        return self.idname_default


    def make_liburl(self, idname, src, request, is_relative):
        """Make a lib url, relative or absolute."""
        if (misc.isabsoluteurl(src)):
            # it's already absolute, just return it
            return src
        if (is_relative):
            src = '${hs::asset_'+idname+'_urlrel}/'+src
        else:
            src = '${hs::asset_'+idname+'_urlabs}/'+src
        # ATTN:TODO resolve it - we should resolve these at startup and not on every request
        src = request.resolve(src)
        # return it
        return src


    def add_script_assetfilepath(self, idname, asset_filepath):
        """Add a script's filepath."""
        # add asset
        assetmanager = self.hscriptmanager.sitecomp_assetmanager()
        mountid = 'internal_assets'
        assetmanager.add_assetsource( massetmanager.MewloAssetSource(id=idname, mountid = mountid, filepath = asset_filepath, namespace='hs') )


    def include(self, request , is_relative=True):
        """Default subclass function; this does the actions needed to register the script for the page so it loads the js and css it needs."""
        idname = self.get_idname()

        # first do any recursive REQUIRED includes
        requires = getattr(self, 'requires', [])
        for requiredlibname in requires:
            self.hscriptmanager.hscript(requiredlibname).include(request, is_relative)

        # add the head items js src includes
        js_src = getattr(self,'js_src', [])
        for src in js_src:
            src = self.make_liburl(idname, src, request, is_relative)
            request.response.add_headitem_js({'src':src})

        # add the head items js script inner includes (raw js code in header)
        js_inner = getattr(self,'js_inner', [])
        for inner in js_inner:
            request.response.add_headitem_js({'_inner':inner})

        # any helper css files?
        css = getattr(self,'css', [])
        for src in css:
            src = self.make_liburl(idname, src, request, is_relative)
            request.response.add_headitem_css({'href':src})





class MewloHScript_JQuery(MewloHScript):
    """JQuery js script."""
    idname_default = 'jquery'
    js_src = ['jquery-2.1.0.js']
    asset_filepath = misc.calc_modulefilepath(__file__)+'/jquery/assets'


class MewloHScript_JQueryCdn(MewloHScript):
    """JQuery js script."""
    idname_default = 'jquery_cdn'
    js_src = ['http://www.google.com/jsapi']
    js_inner = ['google.load("jquery","1.4")']


class MewloHScript_Angular(MewloHScript):
    """Angular js script."""
    idname_default = 'angular'
    js_src = ['angular.js']
    asset_filepath = misc.calc_modulefilepath(__file__)+'/angular/assets'


class MewloHScript_Bootstrap(MewloHScript):
    """bootstrap css script. See http://getbootstrap.com/getting-started/#download"""
    idname_default = 'bootstrap'
    js_src = ['//netdna.bootstrapcdn.com/bootstrap/3.1.1/js/bootstrap.min.js']
    css = ['//netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap.min.css', '//netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap-theme.min.css']


class MewloHScript_Pure(MewloHScript):
    """pure css script. See https://github.com/yui/pure/releases/"""
    idname_default = 'pure'
    css = ['http://yui.yahooapis.com/pure/0.5.0-rc-1/pure-min.css']


class MewloHScript_Foundation(MewloHScript):
    """foundation css script. See http://foundation.zurb.com/develop/download.html"""
    idname_default = 'foundation'
    js_src = ['js/foundation.min.js']
    css = ['css/normalize.css', 'css/foundation.css']
    asset_filepath = misc.calc_modulefilepath(__file__)+'/foundation/assets'








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
        self.register_hscript(MewloHScript_JQuery())
        self.register_hscript(MewloHScript_Angular())
        self.register_hscript(MewloHScript_Bootstrap())
        self.register_hscript(MewloHScript_Pure())
        self.register_hscript(MewloHScript_Foundation())



    def register_hscript(self, hscript):
        """Register javascript libraries internally for later lookup."""
        idname = hscript.get_idname()
        # store it
        self.hscripts[idname] = hscript
        # let it do any startup stuff
        hscript.startup_register(self)




    def add_script_assetfilepath(self, idname, asset_filepath):
        """Add a script's filepath."""
        # add asset
        assetmanager = self.sitecomp_assetmanager()
        mountid = 'internal_assets'
        assetmanager.add_assetsource( massetmanager.MewloAssetSource(id=idname, mountid = mountid, filepath = filepath, namespace='js') )


    def hscript(self, idname):
        """Standard accessor."""
        return self.hscripts[idname]
























