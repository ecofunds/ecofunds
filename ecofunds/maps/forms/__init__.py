# coding: utf-8
from django import forms
from django.utils.translation import gettext as _
from ecofunds.core.models import OrganizationType, Activity, InvestmentType


class OrganizationFilterForm(forms.Form):
    name = forms.CharField(required=False)
    kind = forms.ModelChoiceField(queryset=OrganizationType.objects.all(), required=False, empty_label=_('Choose an organization type'))
    country = forms.CharField(required=False)
    state = forms.CharField(required=False)


class ProjectFilterForm(forms.Form):
    name = forms.CharField(required=False)
    activity = forms.ModelChoiceField(queryset=Activity.objects.all(), required=False, empty_label=_('Choose an activity'))
    country = forms.CharField(required=False)
    state = forms.CharField(required=False)
    organization = forms.CharField(required=False)


class InvestmentFilterForm(forms.Form):
    kind = forms.ModelChoiceField(queryset=InvestmentType.objects.all(), required=False, empty_label=_('Choose an investment type'))
    organization = forms.CharField(required=False)
    project = forms.CharField(required=False)
    country = forms.CharField(required=False)
    state = forms.CharField(required=False)
