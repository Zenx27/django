from django import template
register = template.Library()

@register.filter
def shout(value):
    return str(value).upper() + "!"

@register.simple_tag
def fullname(user):
    return f"{user.first_name} {user.last_name}".strip() or user.username
