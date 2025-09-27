from django import template
register = template.Library()

@register.simple_tag
def greetings():
    return "Привет, это мой кастомный тег!"