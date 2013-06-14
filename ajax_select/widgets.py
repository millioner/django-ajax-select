### -*- coding: utf-8 -*- ####################################################
import random

from ajax_select import get_lookup
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.forms.util import flatatt
from django.template.defaultfilters import escapejs
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.simplejson import dumps


class AutoCompleteSelectWidget(forms.widgets.TextInput):
    """  widget to select a model """
    class Media:
        js = ("ajax_select/js/simple_widget.js", "ajax_select/js/jquery.autocomplete.js" )
        css = {"all": ("ajax_select/css/ajax-selects.css", "ajax_select/css/autocomplete.css")}

    add_link = None

    def __init__(self, channel, help_text='', *args, **kwargs):
        super(forms.widgets.TextInput, self).__init__(*args, **kwargs)
        self.channel = channel
        self.help_text = help_text

    def render(self, name, value, attrs=None):
        value = value or ''
        attrs['class'] = attrs.get('class') or ''
        attrs['class'] += ' autocomplete_text'
        attrs['orig_name'] = name
        final_attrs = self.build_attrs(attrs)
        self.html_id = final_attrs.pop('id', name)

        lookup = get_lookup(self.channel)
        if value:
            objs = lookup.get_objects([value])
            try:
                obj = objs[0]
            except IndexError:
                raise Exception("%s cannot find object:%s" % (lookup, value))
            current_result = mark_safe(lookup.format_item(obj))
        else:
            current_result = ''

        context = {
            'name': name,
            'html_id': self.html_id,
            'lookup_url': reverse('ajax_lookup', kwargs={'channel': self.channel}),
            'current_id': value,
            'current_result': current_result,
            'help_text': self.help_text,
            'extra_attrs': mark_safe(flatatt(final_attrs)),
            'func_slug': self.html_id.replace("-",""),
            'add_link': self.add_link,
            'admin_media_prefix': settings.ADMIN_MEDIA_PREFIX,
            'unique_id': 'autocomplete-select-%s' % random.randint(0, 99999)
        }

        return mark_safe(render_to_string(
            ('autocompleteselect_%s.html' % self.channel, 'autocompleteselect.html'), context)
        )

    def value_from_datadict(self, data, files, name):
        lookup = get_lookup(self.channel)
        added_val = getattr(lookup, 'auto_add', False) and data.get("%s[added]" % name, None)
        if added_val:
            added_obj = lookup.create_from_ajax_string(
                ajax_string=added_val,
                request_data=data,
                form_field_name=name
            )
            return added_obj.pk
        else:
            return long(data.get(name, 0)) or None


class AutoCompleteSelectMultipleWidget(forms.widgets.SelectMultiple):
    """ widget to select multiple models """
    class Media:
        js = ("ajax_select/js/simple_widget.js", "ajax_select/js/jquery.autocomplete.js" )
        css = {"all": ("ajax_select/css/ajax-selects.css", "ajax_select/css/autocomplete.css")}

    def __init__(self, channel, help_text='', show_help_text=False, *args, **kwargs):
        super(AutoCompleteSelectMultipleWidget, self).__init__(*args, **kwargs)
        self.channel = channel
        self.help_text = help_text # admin will also show help. set True if used outside of admin
        self.show_help_text = show_help_text

    def render(self, name, value, attrs=None):
        attrs['class'] = attrs.get('class') or ''
        attrs['class'] += ' autocomplete_text'
        final_attrs = self.build_attrs(attrs)
        self.html_id = final_attrs.pop('id', name)

        lookup = get_lookup(self.channel)
        value = value or []
        return mark_safe(render_to_string(
            ('autocompleteselectmultiple_%s.html' % self.channel, 'autocompleteselectmultiple.html'), {
                'name': name,
                'html_id': self.html_id,
                'lookup_url': reverse('ajax_lookup', kwargs={ 'channel': self.channel }),
                'current': value,
                'current_reprs': mark_safe(dumps([[obj.pk, lookup.format_item(obj)] for obj in lookup.get_objects(value)])),
                'help_text': self.help_text if self.show_help_text else '',
                'extra_attrs': mark_safe(flatatt(final_attrs)),
                'func_slug': self.html_id.replace("-",""),
                'admin_media_prefix': settings.ADMIN_MEDIA_PREFIX,
                'unique_id': 'autocomplete-select-%s' % random.randint(0, 99999)
            }
        ))

    def value_from_datadict(self, data, files, name):
        lookup = get_lookup(self.channel)
        result = []

        added_vals = getattr(lookup, 'auto_add', False) and data.getlist("%s[added]" % name, [])
        if added_vals:
            for added_val in added_vals:
                added_obj = lookup.create_from_ajax_string(
                    ajax_string=added_val,
                    request_data=data,
                    form_field_name=name
                )
            result.append(added_obj.pk)

        for id in data.getlist(name, []):
            result.append(long(id or 0) or None)
        return result

class AutoCompleteWidget(forms.TextInput):
    """
    Widget to select a search result and enter the result as raw text in the text input field.
    the user may also simply enter text and ignore any auto complete suggestions.
    """
    class Media:
        js = ("ajax_select/js/simple_widget.js", "ajax_select/js/jquery.autocomplete.js" )
        css = {"all": ("ajax_select/css/ajax-selects.css", "ajax_select/css/autocomplete.css")}

    channel = None
    help_text = ''
    html_id = ''

    def __init__(self, channel, *args, **kwargs):
        self.channel = channel
        self.help_text = kwargs.pop('help_text', '')
        super(AutoCompleteWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        value = value or ''
        attrs['class'] = attrs.get('class') or ''
        attrs['class'] += ' ajax_select_autocomplete'
        attrs['data-lookup_url'] = reverse('ajax_lookup', args=[self.channel])
        final_attrs = self.build_attrs(attrs)

        context = {
            'current_name': value,
            'help_text': self.help_text,
            'name': name,
            'extra_attrs': mark_safe(flatatt(final_attrs)),
            'unique_id': 'autocomplete-select-%s' % random.randint(0, 99999)
        }

        templates = ('autocomplete_%s.html' % self.channel, 'autocomplete.html')
        return mark_safe(render_to_string(templates, context))