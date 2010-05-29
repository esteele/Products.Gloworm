// KSS replacements in jQuery


// ploneapp namespace
if (ploneapp == undefined) {
    var ploneapp = {};
}

(function($) {
    
    ploneapp.getKSSAttr = function (obj, varname){
        var classes = obj.attr('class').split(' ');
        var classname = 'kssattr-' + varname + '-';
        var i, cls, inherited;
        
        for (i in classes){
            cls = classes[i];
            if(cls.indexOf(classname) >= 0){
                return cls.substring(classname.length, cls.length);
            }
        }
        
        inherited = obj.parents("[class*='" + classname + "']");
        if (inherited.length){
            return ploneapp.getKSSAttr(inherited, varname);
        }

        return '';
    };

    ploneapp.handleKSSResponse = function (response){
        $(response).find('command').each(function(){
                ploneapp.doKSSCommand(this);
        });
    };

    ploneapp.extractSelector = function (command){
        var selector = $(command).attr('selector');
        var selectorType = $(command).attr('selectorType');
        switch (selectorType){
            case 'htmlid':
                return '#' + selector;
            case 'css':
                return selector;
            default:
                return selector;
        }
    };

    ploneapp.doKSSCommand = function (command){
        var selector = ploneapp.extractSelector(command);
        var commandName = $(command).attr('name');
        var html, attributeName, replaceText, name, value;
        
        switch (commandName){
            case 'clearChildNodes':
                $(selector).empty();
                break;
            case 'focus':
                $(selector).focus();
                break;            
            case 'replaceHTML':
                html = $(command).find('param[name="html"]').text();
                $(selector).replaceWith(html);
                break;
            case 'replaceInnerHTML':
                html = $(command).find('param[name="html"]').text();
                $(selector).html(html);
                break;
            case 'setAttribute':
                attributeName = $(command).find('param[name="name"]').text();
                replaceText = $(command).find('param[name="value"]').text();
                $(selector).attr(attributeName, replaceText);   
                break;
            case 'setStyle':
                name = $(command).find('param[name="name"]').text();
                value = $(command).find('param[name="value"]').text();
                $(selector).css(name, value);
                break;
            default:
                if (console) {
                    console.log('No handler for command ' + $(command).attr('name'));
                }
        }
    };


    /* Inline Validation */
    ploneapp.addInlineValidation = function (){
        var wrapper, serviceURL, params, uid;
        
        $('input.blurrable, select.blurrable, textarea.blurrable').blur(function(){
            wrapper = $(this).parents("div[class*='kssattr-atfieldname']");
            serviceURL = $('base').attr('href') + '/' + '@@kssValidateField';
            params = {
                'fieldname': ploneapp.getKSSAttr(wrapper, 'atfieldname'),
                'value': $(this).val()
            };
            uid = ploneapp.getKSSAttr(wrapper, 'atuid');
            if (uid){
                params['uid'] = uid;
            }
            $.get(serviceURL, params, function(data){
                ploneapp.handleKSSResponse(data);
            });
        });
    };

    /* Inline Editing */
    ploneapp.addInlineEditing = function (){
        var serviceURL, params, uid, target;
        
        $('.inlineEditable').click(function(){
            serviceURL = $('base').attr('href') + '/' + '@@replaceField';
            params = {
                'fieldname': ploneapp.getKSSAttr($(this), 'atfieldname'),
                'templateId': ploneapp.getKSSAttr($(this), 'templateId'),
                'macro': ploneapp.getKSSAttr($(this), 'macro'),
                'edit': 'True'
            };
            uid = ploneapp.getKSSAttr($(this), 'atuid');
            if (uid){
                params['uid']=uid;
            }
            target = ploneapp.getKSSAttr($(this), 'target');
            if (target){
                params['target']=target;
            }
            $.get(serviceURL, params, function(data){
                ploneapp.handleKSSResponse(data);
                ploneapp.registerInlineFormControlEvents();
            });
        });
    };

    /* Calendar update */
    ploneapp.addCalendarChange = function (){
        var serviceURL, params;
        
        $('a.kssCalendarChange').click(function(){
            serviceURL = $('base').attr('href') + '/' + '@@refreshCalendar';
            params = {
                'portlethash': ploneapp.getKSSAttr($(this), 'portlethash'),
                'year': ploneapp.getKSSAttr($(this), 'year'),
                'month': ploneapp.getKSSAttr($(this), 'month')
            };
            
            $.get(serviceURL, params, function(data){
                ploneapp.handleKSSResponse(data);
                ploneapp.addCalendarChange();
            });
            return false;
        });
    };

    ploneapp.registerInlineFormControlEvents = function (){
        var serviceURL, fieldname, params, valueSelector;
        var value, templateId, macro, uid, target;
        
        $('form.inlineForm input[name="kss-save"]').click(function(){
            serviceURL = $('base').attr('href') + '/' + '@@saveField';
            fieldname = ploneapp.getKSSAttr($(this), 'atfieldname');
            params = {
                'fieldname': fieldname
            };
        
            valueSelector = "input[name='" + params['fieldname'] + "']";
            value = $(this).parents('form').find(valueSelector).val();
            if (value){
                params['value']={
                    fieldname: value
                };
            }
        
            templateId = ploneapp.getKSSAttr($(this), 'templateId');
            if (templateId){
                params['templateId']=templateId;
            }
        
            macro = ploneapp.getKSSAttr($(this), 'macro');
            if (macro){
                params['macro']=macro;
            }
        
            uid = ploneapp.getKSSAttr($(this), 'atuid');
            if (uid){
                params['uid']=uid;
            }
        
            target = ploneapp.getKSSAttr($(this), 'target');
            if (target){
                params['target']=target;
            }

            $.get(serviceURL, params, function(data){
                ploneapp.handleKSSResponse(data);
            });        
        });
        
        $('form.inlineForm input[name="kss-cancel"]').click(function(){
            ploneapp.cancelInlineEdit(this);
        });
        
        $('input.blurrable, select.blurrable, textarea.blurrable').keypress(function(event){
            if (event.keyCode == 27){
                ploneapp.cancelInlineEdit(this);
            }
        });
    };

    ploneapp.cancelInlineEdit = function (obj){
        var serviceURL = $('base').attr('href') + '/' + '@@replaceWithView';
        var fieldname = ploneapp.getKSSAttr($(obj), 'atfieldname');
        var params = {'fieldname': fieldname,
                      'edit':      true};
        var templateId = ploneapp.getKSSAttr($(obj), 'templateId');

        if (templateId){
            params['templateId']=templateId;
        }
    
        var macro = ploneapp.getKSSAttr($(obj), 'macro');
        if (macro){
            params['macro']=macro;
        }
    
        var uid = ploneapp.getKSSAttr($(obj), 'atuid');
        if (uid){
            params['uid']=uid;
        }
    
        var target = ploneapp.getKSSAttr($(obj), 'target');
        if (target){
            params['target']=target;
        }
        $.get(serviceURL, params, function(data){ploneapp.handleKSSResponse(data);});
    };

    $(function(){
        ploneapp.addInlineValidation();
        ploneapp.addInlineEditing();
        ploneapp.addCalendarChange();
    });



})(jQuery);