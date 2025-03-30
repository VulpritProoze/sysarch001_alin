from django import template
from backend.models import SitinSurvey

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, [])