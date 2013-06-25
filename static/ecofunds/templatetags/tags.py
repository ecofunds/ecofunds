from django import forms
from django import template
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.cache import cache

from cms.models.pagemodel import Page
from cms.templatetags import cms_tags

from babel import numbers
import decimal

register = template.Library()

class SetVarNode(template.Node):
 
    def __init__(self, var_name, var_value):
        self.var_name = var_name
        self.var_value = var_value
 
    def render(self, context):
        try:
            value = template.Variable(self.var_value).resolve(context)
        except template.VariableDoesNotExist:
            value = ""
        context[self.var_name] = value
        return u""

@register.tag
def set_var(parser, token):
    """
        {% set <var_name>  = <var_value> %}
    """
    parts = token.split_contents()
    if len(parts) < 4:
        raise template.TemplateSyntaxError("'set' tag must be of the form:  {% set <var_name>  = <var_value> %}")
    return SetVarNode(parts[1], parts[3])
 
@register.simple_tag
def field_value(form, name):
    """ returns field value """
    value = None
    if hasattr(form, 'cleaned_data') and form.cleaned_data.has_key(name):
        value = form.cleaned_data[name]

    if not value:
        value = form.data.get(name, '')

    if not value:
        value = form.initial.get(name, '')

    return value

@register.filter
def setted_fields(form):
    fields = []
    for field in form.fields:
        if (hasattr(form[field].field, 'widget') and not isinstance(form[field].field.widget, forms.HiddenInput)) or not hasattr(form[field].field, 'widget'):
            value = field_value(form, field)
            if value is not None and value != '':
                fields.append(field)
    return fields

@register.filter
def count_setted_fields(form):
    count = 0
    for field in form.fields:
        if (hasattr(form[field].field, 'widget') and not isinstance(form[field].field.widget, forms.HiddenInput)) or not hasattr(form[field].field, 'widget'):
            value = field_value(form, field)
            if value is not None and value != '':
                count += 1
    return count

@register.simple_tag
def field_label(form, field_name):
    return form[field_name].label

@register.simple_tag(takes_context=True)
def currency(context, value):
    #return '${:20,.2f}'.format(float(value))
    if value is not None:
        request = context.get('request', False)
        return numbers.format_currency(
            float(value),
            numbers.get_currency_symbol('USD', 'en_US'),
            u'\xa4\xa4 #,##0.00', locale=request.LANGUAGE_CODE.replace('-', '_')
        )
    return ''

@register.simple_tag(takes_context=True)
def request_value(context, key):
    return ""

@register.filter
def mod(value, arg):
    return value % arg

@register.filter
def get_sum(list):
    return sum(list)

@register.filter
def count(list):
    return len(list)

@register.inclusion_tag('tags/pagination.html')
def pagination(paginator, show_page_size=False):
    pages = []

    n = paginator.number
    t = paginator.paginator.num_pages
    r = range(t) if t <= 3 else range(3)
    if t <= 3 or n <= 3:
        for i in r:
            pages.append(i+1)
        begin = True
        end = False
    elif t > 3 and n < (t-2):
        pos = n % 3
        pages = [n-1, n, n+1]
        begin = False
        end = False
    elif t > 3 and n >= (t-3):
        pages = [t-2, t-1, t]
        begin = False
        end = True

    return {'paginator': paginator, 'pages':pages, 'begin': begin, 'end':end, 'show_page_size': show_page_size}

@register.inclusion_tag('tags/page_link.html', takes_context=True)
def page_link(context, page_lookup, lang=None, site=None, **kwargs):
    request = context.get('request', False)
    if lang is None:
        lang=request.LANGUAGE_CODE
    lang = lang.lower()

    page = get_page(request, page_lookup, lang, site)

    url = "/%s%s" % (lang, page.get_absolute_url(language=lang))

    result = {'page': page, 'url':url}
    result.update(kwargs)

    if request.current_page != None and request.current_page.id == page.id :
        css = result.get('css')
        if css:
            css += ' '
        else:
            css = ''

        result.update({'css': css +'ativo'})

    return result

@register.simple_tag(takes_context=True)
def page_url(context, page_lookup, params=None, lang=None, site=None):

    request = context.get('request', False)
    if lang is None:
        lang=request.LANGUAGE_CODE

    page = get_page(request, page_lookup, lang, site)
    if page :
        return "/%s%s%s" % (lang.lower(), page.get_absolute_url(language=lang), "?id="+ str(params) if params is not None else "")
    return ""

def get_page(request, page_lookup, lang, site=None):
    site_id = cms_tags.get_site_id(site)
    
    if page_lookup:
        if isinstance(page_lookup, Page):
            return page_lookup
        else:
            cache_key = cms_tags._get_cache_key('tags_page_url', page_lookup, lang, site_id)+'_type:absolute_url'
            page = cache.get(cache_key)
            if not page:
                page = Page.objects.get(site=site_id, reverse_id=page_lookup)
                cache.set(cache_key, page, settings.CMS_CACHE_DURATIONS['content'])

            return page
    else:
        return None