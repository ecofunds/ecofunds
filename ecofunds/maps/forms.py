# coding: utf-8
from django import forms
from django.utils.translation import gettext as _
from ecofunds.crud.models import Organization2, Activity2, Investment2


class OrganizationFilterForm(forms.Form):
    pk = forms.IntegerField(required=False)
    name = forms.CharField(required=False)
    kind = forms.ChoiceField(choices=(('', _('Choose an organization type')),) + Organization2.KINDS, required=False)
    country = forms.CharField(required=False)
    state = forms.CharField(required=False)
    city = forms.CharField(required=False)


class ProjectFilterForm(forms.Form):
    pk = forms.IntegerField(required=False)
    name = forms.CharField(required=False)
    activity = forms.ModelChoiceField(queryset=Activity2.objects.all(), required=False, empty_label=_('Choose an activity'))
    organization = forms.CharField(required=False)
    country = forms.CharField(required=False)
    state = forms.CharField(required=False)
    city = forms.CharField(required=False)


class InvestmentFilterForm(forms.Form):
    pk = forms.IntegerField(required=False)
    kind = forms.ChoiceField(choices=(('', _('Choose an investment type')),) + Investment2.KINDS, required=False)
    organization = forms.CharField(required=False)
    project = forms.CharField(required=False)
    country = forms.CharField(required=False)
    state = forms.CharField(required=False)
    city = forms.CharField(required=False)
