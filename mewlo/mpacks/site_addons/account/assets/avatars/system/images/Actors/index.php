<?php

// Try to handle it with the upper level index.php.  (it should know what to do.)
if (file_exists(dirname(__FILE__) . '/index.php'))
	include (dirname(__FILE__) . '/index.php');
else
	exit;

?>