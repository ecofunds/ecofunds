# coding: utf-8
from django.db import models
from django.conf import settings


class BigIntegerField(models.PositiveIntegerField):
    def db_type(self, connection):
        return 'bigint'


if 'south' in settings.INSTALLED_APPS:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^ecofunds\.geonames\.models\.BigIntegerField"])


class Admin1Code(models.Model):
    code = models.CharField(max_length=6, db_index=True)
    name = models.CharField(max_length=250, db_index=True)
    ascii = models.CharField(max_length=250, db_index=True)
    geonameid = models.PositiveIntegerField(primary_key=True, unique=True)

    def __unicode__(self):
        return self.name


# class Admin2Code(models.Model):
#     code = models.CharField(max_length=32)
#     name = models.CharField(max_length=46)
#
#     def __unicode__(self):
#         return self.name


class GeonameManager(models.Manager):
    def countries(self, *args, **kwargs):
        return self.filter(fcode='PCLI').filter(*args, **kwargs)

    def states(self, *args, **kwargs):
        return self.filter(fcode='ADM1').filter(*args, **kwargs)

    def cities(self, *args, **kwargs):
        return self.filter(fcode='ADM2').filter(*args, **kwargs)


class Geoname(models.Model):
    geonameid = models.PositiveIntegerField(primary_key=True, unique=True)
    name = models.CharField(max_length=200, db_index=True)
    alternates = models.CharField(max_length=250, blank=True, db_index=True)
    fclass = models.CharField(max_length=1, db_index=True)
    fcode = models.CharField(max_length=10, db_index=True)
    country = models.CharField(max_length=2, blank=True, db_index=True)
    cc2 = models.CharField('Alternate Country Code', max_length=60, blank=True)
    admin1 = models.CharField(max_length=20, blank=True, db_index=True)
    admin2 = models.CharField(max_length=80, blank=True, db_index=True)
    admin3 = models.CharField(max_length=20, blank=True, db_index=True)
    admin4 = models.CharField(max_length=20, blank=True, db_index=True)
    population = BigIntegerField(db_index=True, default=0)
    elevation = models.IntegerField(db_index=True)
    topo = models.IntegerField(db_index=True)
    timezone = models.CharField(max_length=30, blank=True)
    moddate = models.DateField('Date of Last Modification')
    latitude = models.FloatField()
    longitude = models.FloatField()

    objects = GeonameManager()

    def __unicode__(self):
        if self.country:
            return "%s - %s" % (self.country, self.name)
        return self.name

    def is_country(self):
        return self.fcode == 'PCLI'
