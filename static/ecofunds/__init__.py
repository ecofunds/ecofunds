from django import template
from inspect import getargspec
from django.template.context import Context
from django.template import Node, generic_tag_compiler, Variable
from django.utils.functional import curry


def inclusion_tag(register, context_class=Context, takes_context=False):
    def dec(func):
        params, xx, xxx, defaults = getargspec(func)
        if takes_context:
            if params[0] == 'context':
                params = params[1:]
            else:
                raise TemplateSyntaxError("Any tag function decorated with takes_context=True must have a first argument of 'context'")

        class InclusionNode(Node):
            def __init__(self, vars_to_resolve):
                self.vars_to_resolve = map(Variable, vars_to_resolve)

            def render(self, context):
                resolved_vars = [var.resolve(context) for var in self.vars_to_resolve]
                if takes_context:
                    args = [context] + resolved_vars
                else:
                    args = resolved_vars

                file_name, extra_context = func(*args)

                from django.template.loader import get_template, select_template
                if not isinstance(file_name, basestring) and is_iterable(file_name):
                    t = select_template(file_name)
                else:
                    t = get_template(file_name)
                self.nodelist = t.nodelist
                new_context = context_class(extra_context, autoescape=context.autoescape)
                # Copy across the CSRF token, if present, because inclusion
                # tags are often used for forms, and we need instructions
                # for using CSRF protection to be as simple as possible.
                csrf_token = context.get('csrf_token', None)
                if csrf_token is not None:
                    new_context['csrf_token'] = csrf_token
                return self.nodelist.render(new_context)

        compile_func = curry(generic_tag_compiler, params, defaults, getattr(func, "_decorated_function", func).__name__, InclusionNode)
        compile_func.__doc__ = func.__doc__
        register.tag(getattr(func, "_decorated_function", func).__name__, compile_func)
        return func
    return dec





