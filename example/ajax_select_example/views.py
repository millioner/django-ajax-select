### -*- coding: utf-8 -*- ####################################################

from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404, redirect

from .forms import BookForm
from .models import Book

def main_page(request, template_name):
    context = {}
    return TemplateResponse(request, template_name, context)

def edit_book(request, template_name, object_id=None):
    object = object_id and get_object_or_404(Book, pk=object_id) or None

    form = BookForm(request.POST or None, instance=object)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(request.get_full_path())

    return TemplateResponse(request, template_name, { 'form': form, 'object': object })