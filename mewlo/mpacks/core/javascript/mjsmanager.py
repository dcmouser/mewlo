"""
mjsmanager.py
helper object for javascript stuff
"""


# mewlo imports
from ..manager import manager
from ..setting.msettings import MewloSettings
from ..eventlog.mevent import EFailure, EException
from ..constants.mconstants import MewloConstants as mconst
from ..helpers import misc
from ..asset import massetmanager





class MewloJavascriptlManager(manager.MewloManager):
    """A helper object that handles all mail sending."""

    # class constants
    description = "Manages javascript use on pages."
    typestr = "core"



    def __init__(self, mewlosite, debugmode):
        """Constructor."""
        super(MewloJavascriptlManager,self).__init__(mewlosite, debugmode)
        #
        self.needs_startupstages([mconst.DEF_STARTUPSTAGE_preassetstuff])
        self.jslibs = {}




    def startup_prep(self, stageid, eventlist):
        """
        This is invoked by site strtup, for each stage specified in startup_stages_needed() above.
        """
        super(MewloJavascriptlManager,self).startup_prep(stageid, eventlist)
        if (stageid == mconst.DEF_STARTUPSTAGE_preassetstuff):
            self.register_jslibs()




    def register_jslibs(self):
        """Register javascript libraries internally for later lookup."""
        # ATTN:TODO make this more dynamic (let plugins register these), support versioning

        # jquery (latest local)
        self.register_jslib('jquery', {
            'js_src': ['jquery-2.1.0.js'],
            #'css': ['mycss.js'],
            })

        # jquery (google older)
        self.register_jslib('jquery_googleold', {
            'js_src': ['http://www.google.com/jsapi'],
            'js_inner': ['google.load("jquery","1.4")'],
            'filepath' : filepath,
            })

        # angular
        self.register_jslib('angular', {
            'js_src': ['angular.js'],
            'filepath' : misc.calc_modulefilepath(__file__)+'/angular/assets',
            })









    def register_jslib(self, libname, propdict):
        """Register javascript libraries internally for later lookup."""
        self.jslibs[libname] = propdict
        #
        # make assets for the js library available
        if (('filepath' in propdict) and propdict['filepath']):
            assetmanager = self.sitecomp_assetmanager()
            idname = libname
            filepath = propdict['filepath']
            mountid = 'internal_assets'
            assetmanager.add_assetsource( massetmanager.MewloAssetSource(id=idname, mountid = mountid, filepath = filepath, namespace='js') )






    def include_jslibrary(self, jslibname, request, is_relative=True):
        """Add/include a js library to page."""
        # src file to use for library
        jslib = self.lookup_jslib(jslibname)
        # add the head items js src includes
        if ('js_src' in jslib):
            for src in jslib['js_src']:
                src = self.make_liburl(jslibname, src, request, is_relative)
                request.response.add_headitem_js({'src':src})
        # add the head items js script inner includes (raw js code in header)
        if ('js_inner' in jslib):
            for inner in jslib['js_inner']:
                request.response.add_headitem_js({'_inner':inner})
        # any helper css files?
        if ('css' in jslib):
            for src in jslib['css']:
                src = self.make_liburl(jslibname, src, request, is_relative)
                request.response.add_headitem_css({'href':src})


    def lookup_jslib(self, jslibname):
        """Get the src filename to use in head item for this library."""
        return self.jslibs[jslibname]


    def make_liburl(self, jslibname, src, request, is_relative):
        """Make a lib url, relative or absolute."""
        if (misc.isabsoluteurl(src)):
            # it's already absolute, just return it
            return src
        if (is_relative):
            src = '${js::asset_'+jslibname+'_urlrel}/'+src
        else:
            src = '${js::asset_'+jslibname+'_urlabs}/'+src
        # ATTN:TODO resolve it - we should resolve these at startup and not on every request
        src = request.resolve(src)
        # return it
        return src