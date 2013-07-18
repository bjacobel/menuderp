from django import template

register = template.Library()


@register.simple_tag
def menuwatch():
    return "<span class='menuwatch'>menuwatch</span>"