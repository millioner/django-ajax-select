### -*- coding: utf-8 -*- ####################################################

from django.conf.urls import patterns, include, url
from django.contrib import admin

from ajax_select_example.models import Book

admin.autodiscover()

urlpatterns = patterns('ajax_select_example.views',
    url(r'^$', 'books_list', {'template_name': 'list.html', 'queryset': Book.objects.all()}, name='main_page'),
    url(r'^edit/(?P<object_id>\d*)', 'edit_book',
        {'template_name': 'edit.html'}, name='edit_book'),

    (r'^ajax_select/', include('ajax_select.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
