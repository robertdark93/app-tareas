from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def hours_display(value):
    if value is None:
        return ''
    try:
        total = float(value)
        h = int(total)
        m = int(round((total - h) * 60))
        if h > 0 and m > 0:
            return f'{h}h {m}m'
        elif h > 0:
            return f'{h}h'
        elif m > 0:
            return f'{m}m'
        return '0h'
    except (ValueError, TypeError):
        return value
