from django import template

register = template.Library()


@register.simple_tag
def menuderp():
    return "<span class='menuderp'>menuderp</span>"