# coding: utf-8
from django import template
from ecofunds.maps.views import format_currency


register = template.Library()


@register.simple_tag(takes_context=True)
def currency(context, value):
    if value is not None:
        return format_currency(value)
    return ''
