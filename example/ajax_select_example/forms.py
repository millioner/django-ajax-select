### -*- coding: utf-8 -*- ####################################################

from django import forms
from django.utils.translation import ugettext_lazy as _

from ajax_select.fields import AutoCompleteSelectMultipleField, AutoCompleteSelectField, AutoCompleteField

from .models import Book

class BookForm(forms.ModelForm):

    publisher = AutoCompleteSelectField('publisher', required=True)
    authors = AutoCompleteSelectMultipleField('author', required=False)

    author_select = AutoCompleteField('author', required=False, label=_('Simple select field'))

    class Meta:
        model = Book