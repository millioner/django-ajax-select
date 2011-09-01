### -*- coding: utf-8 -*- ####################################################

from ajax_select import get_lookup
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.forms.util import flatatt
from django.template.defaultfilters import escapejs
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe


class AutoCompleteSelectWidget(forms.widgets.TextInput):
    """  widget to select a model """
    class Media:
        js = ("ajax_select/js/jquery.autocomplete.js", "ajax_select/js/ajax_select.js")
        css = {"all": ("ajax_select/css/ajax-selects.css", "ajax_select/css/autocomplete.css")}

    add_link = None

    def __init__(self, channel, help_text='', *args, **kwargs):
        super(forms.widgets.TextInput, self).__init__(*args, **kwargs)
        self.channel = channel
        self.help_text = help_text

    def render(self, name, value, attrs=None):

        value = value or ''
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
            'admin_media_prefix': settings.ADMIN_MEDIA_PREFIX
        }

        return mark_safe(render_to_string(
            ('autocompleteselect_%s.html' % self.channel, 'autocompleteselect.html'), context)
        )

    def value_from_datadict(self, data, files, name):
        got = data.get(name, None)
        if got:
            return long(got)
        else:
            return None



class AutoCompleteSelectMultipleWidget(forms.widgets.SelectMultiple):
    """ widget to select multiple models """
    class Media:
        js = ("ajax_select/js/jquery.autocomplete.js", "ajax_select/js/ajax_select.js")
        css = {"all": ("ajax_select/css/ajax-selects.css", "ajax_select/css/autocomplete.css")}

    add_link = None

    def __init__(self, channel, help_text='', show_help_text=False, *args, **kwargs):
        super(AutoCompleteSelectMultipleWidget, self).__init__(*args, **kwargs)
        self.channel = channel
        self.help_text = help_text # admin will also show help. set True if used outside of admin
        self.show_help_text = show_help_text

    def render(self, name, value, attrs=None):

        if value is None:
            value = []

        final_attrs = self.build_attrs(attrs)
        self.html_id = final_attrs.pop('id', name)

        lookup = get_lookup(self.channel)

        current_name = "" # the text field starts empty
        # eg. value = [3002L, 1194L]
        if value:
            current_ids = "|" + "|".join(str(pk) for pk in value) + "|" # |pk|pk| of current
        else:
            current_ids = "|"

        objects = lookup.get_objects(value)

        # text repr of currently selected items
        current_repr_json = []
        for obj in objects:
            repr = lookup.format_item(obj)
            current_repr_json.append('new Array("%s", %s)' % (escapejs(repr), obj.pk))

        current_reprs = mark_safe("new Array(%s)" % ", " . join(current_repr_json))
        if self.show_help_text:
            help_text = self.help_text
        else:
            help_text = ''

        context = {
            'name': name,
            'html_id': self.html_id,
            'lookup_url': reverse('ajax_lookup',kwargs={'channel':self.channel}),
            'current': value,
            'current_name': current_name,
            'current_ids': current_ids,
            'current_reprs': current_reprs,
            'help_text': help_text,
            'extra_attrs': mark_safe(flatatt(final_attrs)),
            'func_slug': self.html_id.replace("-",""),
            'add_link': self.add_link,
            'admin_media_prefix': settings.ADMIN_MEDIA_PREFIX
        }
        return mark_safe(render_to_string(
            ('autocompleteselectmultiple_%s.html' % self.channel, 'autocompleteselectmultiple.html'), context
        ))

    def value_from_datadict(self, data, files, name):
        # eg. u'members': [u'|229|4688|190|']
        lookup = get_lookup(self.channel)
        value = [val for val in data.get(name, '').split('|') if val]
        result = []
        for id in value:
            if '"' in id:
                if getattr(lookup, 'auto_add', False):
                    result.append(lookup.model.add_form_ajax_string(id.replace('"', '')))
            else:
                result.append(long(id))
        return result

class AutoCompleteWidget(forms.TextInput):
    """
    Widget to select a search result and enter the result as raw text in the text input field.
    the user may also simply enter text and ignore any auto complete suggestions.
    """
    class Media:
        js = ("ajax_select/js/jquery.autocomplete.js", "ajax_select/js/ajax_select.js")
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
        final_attrs = self.build_attrs(attrs)
        self.html_id = final_attrs.pop('id', name)

        context = {
            'current_name': value,
            'current_id': value,
            'help_text': self.help_text,
            'html_id': self.html_id,
            'lookup_url': reverse('ajax_lookup', args=[self.channel]),
            'name': name,
            'extra_attrs': mark_safe(flatatt(final_attrs)),
            'func_slug': self.html_id.replace("-", "")
        }

        templates = ('autocomplete_%s.html' % self.channel, 'autocomplete.html')
        return mark_safe(render_to_string(templates, context))