/**
 * imagebrowser js code
 * this javascript code works with a widget on a web page where a user can choose from a large set of images in a nested directory tree
 *
 * @author mouser <mouser@donationcoder.com>
 */


if (jQuery) (function($){
	
	$.extend($.fn, {
		imagebrowser: function(o, h) {

			// Defaults
			if( o.folderEvent == undefined ) o.folderEvent = 'click';
			if( o.loadMessage == undefined ) o.loadMessage = 'Loading, please wait...';
			//if (o.filepaneldiv == undefined) o.filepaneldiv = 'filepaneldiv';
			//if (o.directorypaneldiv == undefined) o.directorypaneldiv = 'directorypaneldiv';
			if (o.root == undefined ) o.root = '';


			$(this).each( function() {
				// download and show images from a directory


				function downloadAndShowImages(c, t, dirunescaped) {
					$(c).addClass('wait');
					$(".imagebrowser.start").remove();
					$.post(o.imagebrowser_ajax_url, { dir: t }, function(data) {
						// downloaded stuff

						$(c).find('.start').html('');
						// we remove the temporary wait message and load up new image contents into image panel
						//$(c).removeClass('wait').append(data);
						$(c).removeClass('wait').html(data);
						// now we are going to bind each image to a click event that we handle
						bindImages(c,dirunescaped);
					});
				}


				function downloadDirectoryTree(c, t) {
					$(c).html('<ul class="imagebrowser "><li class="wait">Please wait while server directory is scanned..<li></ul>');
					$('#'+o.filepaneldiv).addClass('wait');
					$(".imagebrowser.start").remove();
					$.post(o.imagebrowser_ajax_url, { dir: t , mode: "dirtree"}, function(data) {
						// downloaded stuff
						$(c).find('.start').html('');
						// we remove the temporary wait message and load up new image contents into image panel
						$(c).removeClass('wait').html(data);
						// now we re-bind the tree
						bindTree(c);
					});
				}


				// bind the tree li items to click events
				function bindTree(t) {
					$(t).find('LI A').bind(o.folderEvent, function() {
						if( $(this).parent().hasClass('imgbdir') ) {
							// they select directory, so load its contents in image panel
							// select it by adding class imgbselected (and remove from others in this div)
							$(t).find('LI').each(function() {$(this).removeClass('imgbselected');});
							$(this).parent().addClass('imgbselected');
							// now show items in it
							$dir = $(this).attr('rel');
							downloadAndShowImages( $('#'+o.filepaneldiv), escape($dir), $dir );
							}
						//return false;
					});

					restoreSelectedFile(t);

					// Prevent A from triggering the # on non-click events
					if( o.folderEvent.toLowerCase != 'click' ) $(t).find('LI A').bind('click', function() { return false; });
				}




				function restoreSelectedFile(t) {
					// now we try to scroll current directory into view
					var $dirandfile = getLookfordirandfile();
					var $lookfordir = $dirandfile.dir;
					var $lookforfile = $dirandfile.file;
					var $founddir = false;
					var $foundel = null;
					if ($lookfordir != '')
						{
						$(t).find('LI A').each (
							function () {
								$dir = $(this).attr('rel');
								if ($dir==$lookfordir)
									{
									$founddir=true;
									$(t).scrollTo($(this));
									// select it by adding class imgbselected (and remove from others in this div)
									$(t).find('LI').each(function() {$(this).removeClass('imgbselected');});
									$(this).parent().addClass('imgbselected');
									}
							});
						// jump to found dir?
						if ($founddir && $lookfordir!='')
							{
							downloadAndShowImages( $('#'+o.filepaneldiv), escape($lookfordir),$lookfordir );
							}
						}
					}




				// find input field directory
				function getLookfordirandfile() {
					if (o.fileinputfield!=null)
						{
						var $fullfile = $('#'+o.fileinputfield).val();
						if ($fullfile != '')
							{
							// strip off up to last /
							var $val = $fullfile;
							var $pos = $val.lastIndexOf('/');
							if ($pos>-1)
								{
								var $dir = $val.substr(0,$pos+1);
								var $fname = $val.substr($pos+1)
								return {dir : $dir, file : $fname, fullfile: $fullfile };
								}
							}
						}
					return {dir : '', file : '' , fullfile : ''};
					}



				// bind image li items to the input form setting function
				function bindImages(t,dir) {
					$(t).find('LI A').bind(o.folderEvent, function() {
						if( $(this).parent().hasClass('imgbfile') ) {
							// select it by adding class imgbselected (and remove from others in this div)
							$(t).find('LI').each(function() {$(this).removeClass('imgbselected');});
							$(this).parent().addClass('imgbselected');
							//
							// they select a file so we want to load it into edit input
							var $selectedfile =  $(this).attr('rel');
							if (o.fileinputfield!=null)
								{
								$('#'+o.fileinputfield).val($selectedfile);
								}

							}
						return false;
					});


					// if this is current dir of edit field, reselect current image
					// select it by adding class imgbselected (and remove from others in this div)

					var $dirandfile = getLookfordirandfile();
					var $lookfordir = $dirandfile.dir;
					var $lookforfile = $dirandfile.file;
					var $lookforfullfile = $dirandfile.fullfile;
					//alert('in imagebrowserjs lookfordir = '+$lookfordir+' and dir = '+dir);
					if ($lookfordir == dir)
						{
						$(t).find('LI A').each(function() {
							var $selectedfile =  $(this).attr('rel');
							if ($selectedfile == $lookforfullfile)
								{
								$(this).parent().addClass('imgbselected');
								$(t).scrollTo($(this).parent());
								}
							else
								$(this).parent().removeClass('imgbselected');
							});
						}
					else
						{
						$(t).scrollTo(0);
						}

					// Prevent A from triggering the # on non-click events
					if( o.folderEvent.toLowerCase != 'click' ) $(t).find('LI A').bind('click', function() { return false; });
				}


				// initial Loading message
				$('#'+o.filepaneldiv).html('<ul class="imagebrowser start"><li class="wait">' + o.loadMessage + '<li></ul>');
				$('#'+o.filepaneldiv).find('.start').html('');
				$('#'+o.filepaneldiv).removeClass('wait');
				// Get the initial file list?
				downloadDirectoryTree( $('#'+o.directorypaneldiv),escape(o.root));



			});
		}



	});
	

})(jQuery);