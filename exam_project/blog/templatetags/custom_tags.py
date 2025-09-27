from django import template

register = template.Library()

@register.simple_tag
def greetings(name="гость"):
    return f"Привет, {name}!"

@register.filter
def shout(value):
    return str(value).upper()

@register.filter
def highlight(value):
    return f"***{value}***"