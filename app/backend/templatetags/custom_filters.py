from django import template
from datetime import datetime, timezone

register = template.Library()

@register.filter
def time_ago(value):
    now = datetime.now(timezone.utc)
    diff = now - value

    seconds = diff.total_seconds()
    if seconds < 60:
        return f"{int(seconds)} seconds ago"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    else:
        return value.strftime("%b %d, %Y, %I:%M %p ")  # Fallback to date if > 1 day