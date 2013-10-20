# coding: utf-8
from django.db import models
from django.utils.translation import ugettext_lazy as _
from ecofunds.crud.managers import OrganizationSearchManager, ProjectSearchManager, InvestmentSearchManager

from ecofunds.geonames.models import Geoname


class AbstractContact(models.Model):
    url = models.URLField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    fax = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True


class AbstractPlace(models.Model):
    address = models.CharField(max_length=255, blank=True, null=True)
    zipcode = models.CharField(max_length=255, blank=True, null=True)

    country = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=2, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)

    lat = models.FloatField('latitude', blank=True, null=True, help_text='Number on the form 44.3456 or -21.9876')
    lng = models.FloatField('longitude', blank=True, null=True, help_text='Number on the form 44.3456 or -21.9876')

    location = models.ForeignKey(Geoname, null=True)

    class Meta:
        abstract = True


class Organization2(AbstractPlace, AbstractContact):
    KINDS = (
        (1, u'Non-profit'),
        (2, u'Private Company'),
        (3, u'Governamental Agency'),
        (4, u'Bilateral Agency'),
        (5, u'Multilateral Agency'),
        (6, u'South-South Cooperation'),
        (7, u'Network'),
        (8, u'Academic/Research Institute'),
        (9, u'Other'),
    )

    name = models.CharField(max_length=255, db_index=True)
    acronym = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    kind = models.IntegerField(choices=KINDS, db_index=True)
    description = models.TextField(blank=True, null=True)
    director = models.CharField(max_length=255, blank=True, null=True)

    objects = OrganizationSearchManager()

    class Meta:
        ordering = ['name']
        verbose_name = _(u'organization')
        verbose_name_plural = _(u'organizations')
        db_table = 'crud_organization'

    def __unicode__(self):
        return self.name


class Activity2(models.Model):
    name = models.CharField(max_length=255, db_index=True)

    class Meta:
        ordering = ['name']
        verbose_name = _('activity')
        verbose_name_plural = _('activities')
        db_table = 'crud_activity'

    def __unicode__(self):
        return self.name


class Project2(AbstractPlace, AbstractContact):
    KINDS = (
        (1, u'Projeto'),
        (2, u'Programa'),
    )

    name = models.CharField(max_length=255, db_index=True)
    acronym = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    kind = models.IntegerField(choices=KINDS, default=1, db_index=True)
    description = models.TextField(blank=True)
    start_at = models.DateField(null=True)
    end_at = models.DateField(null=True)
    goal = models.TextField(blank=True, null=True)

    organization = models.ForeignKey(Organization2, db_index=True)
    activities = models.ManyToManyField(Activity2)
    geofocus = models.TextField(blank=True)

    objects = ProjectSearchManager()

    class Meta:
        ordering = ['name']
        verbose_name = _(u'project')
        verbose_name_plural = _(u'projects')
        db_table = 'crud_project'

    def __unicode__(self):
        return self.name

    @property
    def activities_names(self):
        return ', '.join([ac.name for ac in self.activities.all()])


class Investment2(models.Model):
    KINDS = (
        (1, _('Donation')),
    )

    funding_organization = models.ForeignKey(Organization2, related_name='investment_funding')
    funding_project = models.ForeignKey(Project2, related_name='investment_funding', null=True, blank=True)
    recipient_organization = models.ForeignKey(Organization2, related_name='investment_recipient')
    recipient_project = models.ForeignKey(Project2, related_name='investment_recipient', null=True, blank=True)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    contributed_at = models.DateField(blank=True, null=True)
    completed_at = models.DateField(blank=True, null=True)
    kind = models.IntegerField(choices=KINDS, db_index=True)

    objects = InvestmentSearchManager()

    class Meta:
        verbose_name = _('investment')
        verbose_name_plural = _('investments')
        db_table = 'crud_investment'
