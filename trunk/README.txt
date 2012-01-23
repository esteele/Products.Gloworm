Products.Gloworm Package Readme

    Overview
        
        A theming introspection tool for Plone.
        
    Credits
        
        Author: WebLion Group, Penn State University "support@weblion.psu.edu":mailto:support@weblion.psu.edu
        
        Release Manager: "Eric Steele":mailto:EricSteele+gloworm@psu.edu, esteele on irc.freenode.net
        
    Requirements
        
        * Requires plone.app.customerize 1.1.2 (included in Plone 3.1.3) or higher
        
        * archetypes.kss 1.4.2 (included in Plone 3.1.5) or higher
        
        Confirmed to work in:
        
        * Firefox 3, 4
        
        * Internet Explorer 7
        
        * Safari 3.1, 4, 5
        
        * Opera 9

    Words of warning

        Both GloWorm and CacheSetup operate through monkeypatches to
        PageTemplate.pt_render(). Installing both on the same instance may cause
        unexpected behavior. GloWorm is intended as a development tool and is best left
        on your development machine.

        
    Using GloWorm
        
        Starting the GloWorm inspector requires three things:
        
        1 The Products.Gloworm package should be installed through the Add/Remove Products page.
        
        2 Zope debug mode must be enabled, either by turning debug mode on in your
           zope.conf file or by running Zope in foreground mode. Note that Zope debug
           mode is not the same as Plone's CSS debug mode. For more information see
           http://plone.org/documentation/manual/theme-reference/tools/debug#toc2.
        
        3 Log in as a site manager.
        
        Once those conditions have been met, an "inspect this page" link will
        appear in the Object Actions section of content objects on your site.
        In a typical Plone installation, this is at the bottom of the page
        content. Clicking this link will open up a new view of the content
        object which includes the GloWorm inspection panel. You may also reach
        this view by appending '@@inspect' to the current page's URL. Please
        note that the HTML content of the GloWorm inspector view is
        drastically different than that of the actual page view, it is
        recommended that you do not use the contents of the inspector view for
        styling purposes.
        
        The inspector panel may be resized by dragging the panel's header up
        or down. The navigation tree may also be resized by dragging left or
        right.
        
        In the the inspector view, clicking on any element of the current page
        will bring up a list of information about that page element, including
        TAL statements (tal:attributes, tal:condition, tal:content,
        tal:replace) and the name of the viewlet or portlet in which it is
        contained.
        
        Click the viewlet name to learn more about that viewlet. Viewlet
        inspection includes the name of the viewlet manager containing the
        viewlet, the ability to show and hide the viewlet, and to the ability
        customize the template.
        
        GloWorm's template customization feature utilizes Plone's
        portal_view_customizations utility to manage viewlet templates. To find
        your customized templates in the Zope Management Interface, go to
        "portal_view_customizations" within your Plone site and select the
        "contents" tab.
        
        In the viewlet inspection view, click the viewlet manager name to
        inspect that viewlet manager and the viewlets it contains. A green
        check mark next to a viewlet name indicates that the viewlet is
        visible, while a red "X" indicates that it is hidden. Clicking these
        icons will toggle the visibility of the viewlet accordingly. Clicking
        the up and down arrows performs viewlet reordering. Clicking the name
        of a viewlet will take you to the viewlet inspection view for that
        viewlet.
        
        The navigation tree at the right of the inspector panel provides a
        tree-structured view of the inspected content object's viewlet managers
        and viewlets. Note that the navigation tree will display viewlet
        managers and viewlets that are not within the page's <body> tag (ie.
        "plone.htmlhead"). These may be inspected, but will not be highlighted
        in the page content panel.
        
        Click the red "close" icon in the upper-right corner of the GloWorm
        panel to return to normal site browsing.
    
    Support
        
        Contact WebLion at "support@weblion.psu.edu":mailto:support@weblion.psu.edu, or visit our IRC channel: #weblion
        on freenode.net.
        

Till glowworms light owl-watchmen's flight
Through our green metropolis.
- William Allingham, Greenwood Tree