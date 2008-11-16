plone.app.gloworm Package Readme
=========================

Overview
--------

A Firebug-like inspector tool for Plone.

Credits
-------

Author: WebLion Group, Penn State University <support@weblion.psu.edu>.

Requirements
------------

Requires plone.app.customerize 1.1.2 (included in Plone 3.1.3) or higher.

Confirmed working in:
    * Firefox 3
    * Internet Explorer 7
    * Safari 3.1
    * Opera 9

Using GloWorm
-------------

Install the plone.app.gloworm package through the Add/Remove Products page.
Once installed and when running in Zope debug mode (either by turning
debug mode on in your zope.conf file or by running Zope in foreground mode),
an "inspect this page" link will appear in the Object Actions section of
content objects on your site. Clicking this link will open up a new view of
the page which includes the GloWorm inspection panel. (You may also reach this
view by appending '@@inspect' to the current page's URL).

In this view, clicking on any element of the current page will bring up a list
of information about that object, including TAL commands and the viewlet or
portlet is contained in.

Click the viewlet name to inspect that viewlet. Viewlet inspection includes
the ability to customize the template and to move viewlets from one viewlet
manager to another.

In the viewlet inspection view, click the viewlet manager name to inspect that
viewlet manager. Clicking the lightbulb icon shows or hides the viewlet.
Clicking the up and down arrows allows viewlet reordering. Clicking the name
of a viewlet will take you to the viewlet inspection view for that viewlet.

Click the "close" icon in the upper-right corner of the GloWorm panel to
return to normal browsing.

Support
-------

Contact WebLion at support@weblion.psu.edu, or visit our IRC channel: #weblion
on freenode.net.

Bug reports at http://weblion.psu.edu/trac/weblion/newticket