### -*- coding: utf-8 -*- ####################################################

from ajax_select import get_lookup
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from .widgets import AutoCompleteWidget, AutoCompleteSelectWidget, AutoCompleteSelectMultipleWidget


class AutoCompleteSelectField(forms.fields.CharField):
    """  form field to select a model for a ForeignKey db field """
    channel = None

    def __init__(self, channel, *args, **kwargs):
        self.channel = channel
        widget = kwargs.get("widget", False)
        if not widget or not isinstance(widget, AutoCompleteSelectWidget):
            kwargs["widget"] = AutoCompleteSelectWidget(channel=channel,
                help_text=kwargs.get('help_text', _('Enter text to search.'))
            )
        super(AutoCompleteSelectField, self).__init__(max_length=255, *args, **kwargs)

    def clean(self, value):
        if value:
            lookup = get_lookup(self.channel)
            objs = lookup.get_objects([value])
            if len(objs) != 1:
                raise forms.ValidationError(u"%s cannot find object: %s" % (lookup,value))
            return objs[0]
        else:
            if self.required:
                raise forms.ValidationError(self.error_messages['required'])
            return None

    def check_can_add(self, user, model):
        _check_can_add(self, user, model)

#    def prepare_value(self, value):
#        import pdb; pdb.set_trace()
#        return value


class AutoCompleteSelectMultipleField(forms.CharField):
    """
    form field to select multiple models for a ManyToMany db field
    """

    channel = None

    def __init__(self, channel, *args, **kwargs):
        self.channel = channel
        # admin will also show help text, so by default do not show it in widget
        # if using in a normal form then set to True so the widget shows help
        kwargs['widget'] = AutoCompleteSelectMultipleWidget(
            channel=channel,
            help_text=kwargs.get('help_text', _('Enter text to search.')),
            show_help_text=kwargs.get('show_help_text', False)
        )
        super(AutoCompleteSelectMultipleField, self).__init__(*args, **kwargs)

    def clean(self, value):
#        import pdb; pdb.set_trace()
        if not value and self.required:
            raise forms.ValidationError(self.error_messages['required'])
        return value # a list of IDs from widget value_from_datadict

    def check_can_add(self, user, model):
        _check_can_add(self, user, model)

    def prepare_value(self, value):
#        import pdb; pdb.set_trace()
        return value

    def to_python(self, value):
#        import pdb; pdb.set_trace()
        return value



class AutoCompleteField(forms.CharField):
    """
    Field uses an AutoCompleteWidget to lookup possible completions using a channel and stores raw text (not a foreign key)
    """
    channel = None

    def __init__(self, channel, *args, **kwargs):
        self.channel = channel

        widget = AutoCompleteWidget(channel,help_text=kwargs.get('help_text', _('Enter text to search.')))

        defaults = {'max_length': 255,'widget': widget}
        defaults.update(kwargs)

        super(AutoCompleteField, self).__init__(*args, **defaults)


def _check_can_add(self, user, model):
    """ check if the user can add the model, deferring first to the channel if it implements can_add() \
        else using django's default perm check. \
        if it can add, then enable the widget to show the + link
    """
    lookup = get_lookup(self.channel)
    try:
        can_add = lookup.can_add(user, model)
    except AttributeError:
        ctype = ContentType.objects.get_for_model(model)
        can_add = user.has_perm("%s.add_%s" % (ctype.app_label,ctype.model))
    if can_add:
        self.widget.add_link = reverse('add_popup', kwargs={
            'app_label': model._meta.app_label, 'model': model._meta.object_name.lower()
        })

def autoselect_fields_check_can_add(form,model,user):
    """ check the form's fields for any autoselect fields
        and enable their widgets with + sign add links if permissions allow
    """
    for name, form_field in form.declared_fields.iteritems():
        if isinstance(form_field, (AutoCompleteSelectMultipleField, AutoCompleteSelectField)):
            db_field = model._meta.get_field_by_name(name)[0]
            form_field.check_can_add(user, db_field.rel.to)