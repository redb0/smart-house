from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
def addstr(value, arg):
    # if arg != '':
    return value + arg
    # return value
    # return value.join(arg)

# register.filter(name='addstr', filter_func=addstr)
