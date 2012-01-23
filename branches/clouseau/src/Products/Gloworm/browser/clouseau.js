function startClouseauSession() {
    // hide the javascript warning
    var warning = document.getElementById("clouseau-warning");
    warning.style.display = "none";
    
    // would be helpful if we could hide this in the pt, oh well.
    var left = document.getElementById("portal-column-one")
    if (left) {
        left.style.display = "none";
    }
    
    
    _session_id = getString("session_id");
    _context = getString("context");
    if (_session_id != "null") {
        // yay start the check status loop
        gotSession();
        return;
    }
    
    var req = new XMLHttpRequest()
    req.onreadystatechange = function() {
        if(req.readyState == 4) {
            if (req.status != 200) {
                setMessage("Error occured trying to create new session: " + req.statusText + " (" + req.status + ")." , "error");
            } else {
                var xml = req.responseXML.documentElement;
                var session = xml.getElementsByTagName("session")[0];
                _session_id = session.getAttribute("id");
                gotSession();
                loadFilename();
            };
        };
    };
    req.open("POST", "clouseau_tool/new_session_xml", true);
    req.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    req.send("context=/gloworm/front-page");
    setMessage("Getting a session with context of " + _context + " please wait...");
    setTimeout(reFocus, 0);
}

startClouseauSession();