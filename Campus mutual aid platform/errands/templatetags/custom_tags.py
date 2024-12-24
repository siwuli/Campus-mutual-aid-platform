# errands/templatetags/custom_tags.py

from django import template

register = template.Library()

@register.filter
def average_rating(reviews):
    avg = reviews.aggregate(Avg('rating'))['rating__avg']
    return round(avg, 2) if avg else 0
