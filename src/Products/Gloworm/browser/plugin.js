kukit.actionsGlobalRegistry.register('scrollNavTree', function(oper) {
;;; oper.componentName = '[scrollNavTree] action';
;;; oper.evaluateParameters([], {});
    var itemScrollPos = oper.node.parentNode.offsetTop;
    var maxDistanceFromEdge = 75;
    scrollElement = document.getElementById('glowormPanelNavTree').parentNode;
    
    visibleTop = scrollElement.scrollTop;
    visibleBottom = visibleTop + scrollElement.offsetHeight;
    if (!((itemScrollPos > visibleTop + maxDistanceFromEdge) && (itemScrollPos < visibleBottom - maxDistanceFromEdge))){
        var att = { scroll: { to: [0, itemScrollPos - parseInt(scrollElement.offsetHeight/2)]}};
        var yanim = new YAHOO.util.Scroll(scrollElement, att);
        yanim.animate();
    }
});
kukit.commandsGlobalRegistry.registerFromAction('scrollNavTree', 
                                                kukit.cr.makeSelectorCommand);

kukit.actionsGlobalRegistry.register('scrollContentArea', function(oper) {
;;; oper.componentName = '[scrollContentArea] action';
;;; oper.evaluateParameters([], {});
    var itemScrollPos = oper.node.offsetTop;
    var maxDistanceFromEdge = 75;
    scrollElement = document.getElementById('glowormPageWrapper').parentNode;

    visibleTop = scrollElement.scrollTop;
    visibleBottom = visibleTop + scrollElement.offsetHeight;
    if (!((itemScrollPos > visibleTop + maxDistanceFromEdge) && (itemScrollPos < visibleBottom - maxDistanceFromEdge))){
        var att = { scroll: { to: [0, itemScrollPos - parseInt(scrollElement.offsetHeight/2)]}};
        var yanim = new YAHOO.util.Scroll(scrollElement, att);
        yanim.animate();
    }
});
kukit.commandsGlobalRegistry.registerFromAction('scrollContentArea', 
                                                kukit.cr.makeSelectorCommand);
                                                
var _ParseTALAttributes = function() {
    this.check = function(attrs, node){};
    this.eval = function(attrs, node) {
        attrs = kukit.dom.getRecursiveAttribute(node, 'tal:attributes', false, kukit.dom.getAttribute);
        retArray = [];        
        if(attrs){
            splitAttrs = attrs.split(';');
            for(s=0; s < splitAttrs.length; s++){
                // Pull out a tal:attribute and trim any whitespace
                line = splitAttrs[s].replace(/^\s+|\s+$/g, '');
                // Ignore any blank items
                if(line.length > 0){
                    // Pull out the individual bits
                    attribute = line.split(' ')[0];
                    expression = line.split(' ')[1];
                    // Look up the result
                    result = kukit.dom.getRecursiveAttribute(node, attribute, false, kukit.dom.getAttribute);
                    // alert([attribute, expression, result]);
                    // Append it to the return array
                    retArray.push([attribute, expression, result]);
                }
            }
        }
        // alert("retarray: " + retArray);
        return retArray;
   };
};

kukit.pprovidersGlobalRegistry.register('parseTALAttributes', _ParseTALAttributes);

var _GetSourceAnnotation = function() {
  this.check = function(attrs, node){};
  this.eval = function(attrs, node) {
      siblingNode = node;
      parentalNode = node.parentNode;
      while(parentalNode){
          while(siblingNode){
              if ((siblingNode.nodeType == document.COMMENT_NODE) && (siblingNode.data.indexOf('==============================================================================') != -1)){
                  return siblingNode.data;
              }          
              siblingNode = siblingNode.previousSibling;
          }
          siblingNode = parentalNode;
          parentalNode = parentalNode.parentNode;
      }
      return '';
  };
};
kukit.pprovidersGlobalRegistry.register('sourceAnnotation', _GetSourceAnnotation);

kukit.actionsGlobalRegistry.register("showErrorMessage", function(oper) {
    /* Show an error message panel
    */
    errorMessage = oper.parms.message
    YAHOO.namespace("gloworm.alert");
    YAHOO.gloworm.alert.errorPanel = new YAHOO.widget.Panel("glowormErrorPanel", { width:"450px",
                                                                                   visible:true,
                                                                                   draggable:true,
                                                                                   close:true,
                                                                                   constraintoviewport:true,
                                                                                   autofillheight: "body"} );
    YAHOO.gloworm.alert.errorPanel.setHeader("Error");
    YAHOO.gloworm.alert.errorPanel.setBody("<p>The following error occured: <pre>" + errorMessage + "</pre></p>");
    YAHOO.gloworm.alert.errorPanel.setFooter("");
    YAHOO.gloworm.alert.errorPanel.render(document.body);

    var resize = new YAHOO.util.Resize("glowormErrorPanel", { handles: ["br"],
                                                              autoRatio: false,
                                                              minWidth: 300,
                                                              minHeight: 100,
                                                              status: false });

    resize.on("startResize", function(args) {

	    if (this.cfg.getProperty("constraintoviewport")) {
            var D = YAHOO.util.Dom;

            var clientRegion = D.getClientRegion();
            var elRegion = D.getRegion(this.element);

            resize.set("maxWidth", clientRegion.right - elRegion.left - YAHOO.widget.Overlay.VIEWPORT_OFFSET);
            resize.set("maxHeight", clientRegion.bottom - elRegion.top - YAHOO.widget.Overlay.VIEWPORT_OFFSET);
        } else {
            resize.set("maxWidth", null);
            resize.set("maxHeight", null);
    	}

    }, YAHOO.gloworm.alert.errorPanel, true);

    
    resize.on("resize", function(args) {
        var panelHeight = args.height;
        this.cfg.setProperty("height", panelHeight + "px");
    }, YAHOO.gloworm.alert.errorPanel, true);
    

    
});
kukit.commandsGlobalRegistry.registerFromAction('showErrorMessage',
    kukit.cr.makeGlobalCommand);



kukit.actionsGlobalRegistry.register('forceGlowormPanelResize', function() {
    GloWormPanel.resize();
});
kukit.commandsGlobalRegistry.registerFromAction('forceGlowormPanelResize', kukit.cr.makeGlobalCommand);
