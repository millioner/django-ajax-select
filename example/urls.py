### -*- coding: utf-8 -*- ####################################################

from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.views.generic.list_detail import object_list

from ajax_select_example.models import Book

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', object_list, {'template_name': 'list.html', 'queryset': Book.objects.all()}, name='main_page'),
    url(r'^edit/(?P<object_id>\d*)', 'ajax_select_example.views.edit_book',
        {'template_name': 'edit.html'}, name='edit_book'),
    url(r'^save/', 'ajax_select_example.views.save_book', name='save_book'),

    (r'^ajax_select/', include('ajax_select.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
