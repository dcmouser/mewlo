"""
mcontroller_imagebrowsers.py
Controller made to respond to image browsing ajax widgets.
ATTN:TODO - options for showing extensions, don't capitalize extensions, filter by extensions
"""


# mewlo imports
import mcontroller

# python imports
import os
import urllib




class MewloController_ImageBrowser(mcontroller.MewloController):
    """
    The MewloController_ImageBrowser class handles requests for static files
    """

    def __init__(self, assetsource_id, asset_subdir):
        # Invoke parent init and tell it to invoke our local controller_call when triggered
        super(MewloController_ImageBrowser,self).__init__(function = self.controller_call)
        self.assetsource_id = assetsource_id
        self.asset_subdir = asset_subdir



    def controller_call(self, request):
        """The controller callable function -- respond to image browsing requests."""

        # get post data
        dir_requested = request.get_postdata_val('dir')
        mode_requested = request.get_postdata_val('mode')

        dir_requested = urllib.unquote(dir_requested)

        flag_showextensions = True
        allowed_extension_list = ['jpg','jpeg','gif','png','tif','tiff','pcx','bmp']

        # invoke helper function for tree or other modes
        #print "ATTN: in MewloController_ImageBrowser with {0},{1}".format(dir_requested,mode_requested)
        if (mode_requested == 'dirtree'):
            reth = self.respond_for_image_chooser(request, dir_requested, True, False, True, False, False, flag_showextensions, allowed_extension_list)
        else:
            reth = self.respond_for_image_chooser(request, dir_requested, False, True, False, True, True, flag_showextensions, allowed_extension_list)

        # now set response to raw reth (since it's ajax result)
        #print "RAW AJAX RESULT SENDING '{0}'.".format(reth)
        request.response.set_direct_passthrough(True)
        request.response.set_responsedata(reth)



    def respond_for_image_chooser(self, request, dir_requested, flag_showdirs, flag_showfiles, flag_recurse, flag_sayempty, flag_showimages, flag_showextensions, allowed_extension_list):
        # respond with a list of directories or images
        reth = ''
        dircount = 0
        filecount = 0

        # source file dir
        assetmanager = request.mewlosite.comp('assetmanager')
        root_filepath = assetmanager.calc_source_filepath(self.assetsource_id, self.asset_subdir)
        root_fileurl = assetmanager.calc_source_urlpath(self.assetsource_id, self.asset_subdir)
        #print "Serving files from '{0}' via url '{1}'.".format(root_filepath, root_fileurl)

        # ATTN: TODO - security protection for this constructed path
        filepath = root_filepath + dir_requested

        #print "FILEPATH req = '{0}'.".format(filepath)

        if (os.path.isdir(filepath)):
            # path exists
            dircontents = os.listdir(filepath)
            if (len(dircontents)>0):
                reth += '<ul class="imagebrowser" style="">'
                if (flag_showdirs):
                    # walk dirs
                    for fpath in dircontents:
                        fpathfull = os.path.join(filepath, fpath)
                        dir_rel = dir_requested + '/' + fpath
                        if (os.path.isdir(fpathfull)):
                            # we found a dir
                            caption = self.calc_filecaption_frompath(fpath)
                            reth += '<li class="imgbdir"><a href="#" rel="{0}">'.format(dir_rel) + caption + '</a>'
                            if (flag_recurse):
                                # recurse indo dir
                                reth += self.respond_for_image_chooser(request, dir_rel, flag_showdirs, flag_showfiles, flag_recurse, flag_sayempty, flag_showimages, flag_showextensions, allowed_extension_list)
                            reth += '</li>\n'
                            dircount += 1
                if (flag_showfiles):
                    # walk files
                    for fpath in dircontents:
                        fpathfull = os.path.join(filepath, fpath)
                        dir_rel = dir_requested + '/' + fpath
                        if (os.path.isfile(fpathfull)):
                            # we found a file
                            # split into base and extension
                            (filename,extension) = os.path.splitext(fpath)
                            # standardize extension
                            if (len(extension)>0):
                                extension=extension[1:].lower()
                            # is it allowed file
                            if (allowed_extension_list and (not extension in allowed_extension_list)):
                                # not in list, skip
                                continue
                            # generate nice caption
                            caption = self.calc_filecaption_frompath(filename)
                            # add back extension to caption?
                            if (flag_showextensions):
                                caption += "."+extension
                            if (flag_showimages):
                                urlpath = root_fileurl + dir_rel
                                reth += '<li class="imgbfile"><a href="#" rel="{0}">'.format(dir_rel)
                                reth += '<div class="imgbblock"><img src="{0}" class="imgbfile"/><br/>'.format(urlpath)
                                reth += caption + '<br/><br/></div></a></li>\n'
                            else:
                                reth += '<li class="imgbfile"><a href="#" rel="{0}">'.format(dir_rel)
                                reth += caption + '</a></li>\n'
                            filecount += 1
                reth += '</ul>'

        if (flag_sayempty and (filecount+dircount==0)):
            reth += '<li class="imgbfile">No files found.</li>\n'

        return reth



    def calc_filecaption_frompath(self, fpath):
        """Make a caption for a file"""
        caption = fpath
        caption = caption.replace('_',' ')
        caption = caption.title()
        return caption
















