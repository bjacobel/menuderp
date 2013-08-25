/*  
    ONLY SITE-WIDE SCRIPTS go in this file. Anything else should go into
    {% footer_scripts %} blocks in the views it needs to run on.
*/

$(document).ready(function() {
    // set focus on first text field of any page
     $("input:text:visible:first").focus();
});