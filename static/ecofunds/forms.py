from django import forms
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _
import datetime


class AdvancedSearchForm(forms.Form):
    page = forms.IntegerField(widget=forms.HiddenInput())
    list_type = forms.IntegerField(widget=forms.HiddenInput(attrs={'value': 1}))
    order_by = forms.CharField(widget=forms.HiddenInput())
    
