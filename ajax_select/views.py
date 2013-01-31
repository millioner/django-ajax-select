### -*- coding: utf-8 -*- ####################################################

from django.db import models
from django.http import HttpResponse
from django.utils.translation import ugettext
from django.contrib.admin import site

from ajax_select import get_lookup

def ajax_lookup(request, channel):
    """ this view supplies results for both foreign keys and many to many fields """
    if 'q' not in request.REQUEST:
        return HttpResponse('') # suspicious
    query = request.REQUEST['q']

    lookup_channel = get_lookup(channel)
    
    if query:
        instances = lookup_channel.get_query(query, request)
    else:
        instances = []

    results = []
    for item in instances:
        itemf = lookup_channel.format_item(item)
        itemf = itemf.replace("\n", "").replace("|", "&brvbar;")
        resultf = lookup_channel.format_result(item)
        resultf = resultf.replace("\n", "").replace("|", "&brvbar;")
        results.append("|".join((unicode(item.pk), itemf, resultf)))

    if lookup_channel.auto_add and 'no_add' not in request.REQUEST:
        results.append("|".join((u'0', query, ugettext('Add as new item'))))
    return HttpResponse("\n".join(results) )


def add_popup(request,app_label,model):
    """ present an admin site add view, hijacking the result if its the dismissAddAnotherPopup js and returning didAddPopup """ 
    the_model = models.get_model(app_label, model)
    admin = site._registry[the_model]

    admin.admin_site.root_path = "/ajax_select/" # warning: your URL should be configured here. 
    # as in your root urls.py includes :
    #    (r'^ajax_select/', include('ajax_select.urls')),
    # I should be able to auto-figure this out but ...

    response = admin.add_view(request,request.path)
    if request.method == 'POST':
        if response.content.startswith('<script type="text/javascript">opener.dismissAddAnotherPopup'):
            return HttpResponse( response.content.replace('dismissAddAnotherPopup', 'didAddPopup' ) )
    return response

