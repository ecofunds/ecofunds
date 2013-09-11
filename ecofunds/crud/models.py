# coding: utf-8
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Contact(models.Model):
    url = models.URLField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    fax = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True


class Place(models.Model):
    address = models.CharField(max_length=255, blank=True, null=True)
    zipcode = models.CharField(max_length=255, blank=True, null=True)

    country = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=2, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)

    lat = models.FloatField(blank=True, null=True)
    lng = models.FloatField(blank=True, null=True)

    class Meta:
        abstract = True


class Organization(Place, Contact):
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

    name = models.CharField(max_length=255)
    acronym = models.CharField(max_length=255, blank=True, null=True)
    kind = models.IntegerField(choices=KINDS)
    description = models.TextField(blank=True, null=True)
    director = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = _(u'organization')
        verbose_name_plural = _(u'organizations')

    def __unicode__(self):
        return self.name


class Activity(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = _('activity')
        verbose_name_plural = _('activities')

    def __unicode__(self):
        return self.name


class Project(Place, Contact):
    KINDS = (
        (1, u'Projeto'),
        (2, u'Programa'),
    )

    name = models.CharField(max_length=255)
    acronym = models.CharField(max_length=255, blank=True, null=True)
    kind = models.IntegerField(choices=KINDS, default=1)
    description = models.TextField(blank=True)
    start_at = models.DateField(null=True)
    end_at = models.DateField(null=True)
    goal = models.TextField(blank=True, null=True)

    organization = models.ForeignKey(Organization)
    activities = models.ManyToManyField(Activity)
    geofocus = models.TextField(blank=True)

    class Meta:
        verbose_name = _(u'project')
        verbose_name_plural = _(u'projects')

    def __unicode__(self):
        return self.name


class Investment(models.Model):
    KINDS = (
        (1, _('Donation')),
    )

    funding_organization = models.ForeignKey(Organization, related_name='investment_funding')
    funding_project = models.ForeignKey(Project, related_name='investment_funding', null=True, blank=True)
    recipient_organization = models.ForeignKey(Organization, related_name='investment_recipient')
    recipient_project = models.ForeignKey(Project, related_name='investment_recipient', null=True, blank=True)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    contributed_at = models.DateField(blank=True, null=True)
    completed_at = models.DateField(blank=True, null=True)
    kind = models.IntegerField(choices=KINDS)

    class Meta:
        verbose_name = _('investment')
        verbose_name_plural = _('investments')
