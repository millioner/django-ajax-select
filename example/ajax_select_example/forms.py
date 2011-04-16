### -*- coding: utf-8 -*- ####################################################

from django import forms
from django.utils.translation import ugettext_lazy as _

from ajax_select.fields import AutoCompleteSelectMultipleField, AutoCompleteSelectField

from .models import Book

class BookForm(forms.ModelForm):

    publisher = AutoCompleteSelectField('publisher', required=True)
    authors = AutoCompleteSelectMultipleField('author', required=False)
    class Meta:
        model = Book