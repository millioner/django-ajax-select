### -*- coding: utf-8 -*- ####################################################
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Author(models.Model):
    """
    Author model
    >>> obj, created = Author.objects.get_or_create(first_name='Jule', last_name='Verne', notes='Great writer')
    >>> obj
    <Author: Jule Verne>
    """
    first_name = models.CharField(max_length=255, verbose_name=_('First name'))
    last_name = models.CharField(max_length=255, verbose_name=_('First name'))
    notes = models.TextField(_('Some notes'))

    class Meta:
        verbose_name = _("autor")
        verbose_name_plural = _("autors")
        ordering = ('first_name',)

    def __unicode__(self):
        return '%s %s' % (self.first_name, self.last_name)

class Publisher(models.Model):
    """
    Publisher model
    >>> obj, created = Publisher.objects.get_or_create(name='Apress', address='Somewhere in USA')
    >>> obj
    <Publisher: Apress>
    """
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    address = models.TextField(_('Address'))

    class Meta:
        verbose_name = _("publisher")
        verbose_name_plural = _("publishers")
        ordering = ('name',)

    def __unicode__(self):
        return self.name

class Book(models.Model):
    """
    Book model
    >>> import datetime
    >>> publisher, created = Publisher.objects.get_or_create(name='Apress', address='Somewhere in USA')
    >>> author, created = Author.objects.get_or_create(first_name='Jule', last_name='Verne', notes='Great writer')
    >>> obj, created = Book.objects.get_or_create(title='Captain Nemo', release_date=datetime.date.today(), publisher=(publisher, ), author=author)
    >>> obj
    <Book: Captain Nemo>
    """
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    release_date = models.DateField(_('Release date'))
    publisher = models.ForeignKey('Publisher', verbose_name=_('Publisher'))
    authors = models.ManyToManyField('Author', verbose_name=_('Authors'))

    class Meta:
        verbose_name = _("book")
        verbose_name_plural = _("books")
        ordering = ('title',)

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('edit_book', (), {'object_id': self.pk})