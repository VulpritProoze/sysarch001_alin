from django import template
from django.utils import timezone

register = template.Library()

@register.filter
def time_ago(value):
    if not value:
        return ""
    
    now = timezone.localtime(timezone.now())
    value = timezone.localtime(value)

    diff = now - value

    seconds = diff.total_seconds()
    
    # Handle future dates (negative seconds) by returning formatted date
    if seconds < 0:
        return value.strftime("%b %d, %Y, %I:%M %p")
    
    if seconds < 60:
        return f"{int(seconds)} seconds ago"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    else:
        return value.strftime("%b %d, %Y, %I:%M %p")