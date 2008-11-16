Products.Gloworm Package Readme
=========================

Overview
--------

A Firebug-like inspector tool for Plone.

Credits
-------

Author: WebLion Group, Penn State University <support@weblion.psu.edu>.

Requirements-
------------

Requires Plone 3.1.3 or higher.

Using GloWorm
-------------

Install the Products.Gloworm package through the Add/Remove Products page. Once installed and when 
running in Zope debug mode, an "inspect this page" link will appear in the Object Actions section of
content objects on your site. Clicking this link will open up a new view of the page which includes
the GloWorm inspection panel. (You may also reach this view by appending '@@inspect' to the current 
page's URL).

In this view, clicking on any element of the current page will bring up a list of information about 
that object, including TAL commands and the viewlet or portlet is contained in.

Click the viewlet name to inspect that viewlet. Viewlet inspection includes the ability to customize
the template and to move viewlets from one viewlet manager to another.

In the viewlet inspection view, click the viewlet manager name to inspect that viewlet manager. 
Clicking the lightbulb icon shows or hides the viewlet. Clicking the up and down arrows allows viewlet
reordering. Clicking the name of a viewlet will take you to the viewlet inspection view for that viewlet.

Click the "close" icon in the upper-right corner of the GloWorm panel to return to normal browsing.

