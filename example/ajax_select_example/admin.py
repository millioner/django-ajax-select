### -*- coding: utf-8 -*- ####################################################

from django.contrib import admin

from ajax_select import make_ajax_form

from .models import Book, Author, Publisher

class AuthorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name',)
    search_fields = ('first_name', 'last_name')

admin.site.register(Author, AuthorAdmin)

class PublisherAdmin(admin.ModelAdmin):
    list_display = ('name', 'address',)
    search_fields = ('name', 'address',)

admin.site.register(Publisher, PublisherAdmin)

class BookAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)
    form = make_ajax_form(Book, { 'authors': 'author', 'publisher': 'publisher'})

admin.site.register(Book, BookAdmin)