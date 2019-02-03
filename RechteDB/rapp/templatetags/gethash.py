from django import template
register = template.Library()

# Liefert einen Wert eines Hashes für die Templates
@register.filter
def hash(h, key):
    if key in h:
        return h[key]
    return h

#Liefert den Zweck einer Rolle (ist der zweite Teil des Tupels)
@register.filter
def finde(inputset, search):
    for s in inputset:
        (name, zweck) = s
        if name == search:
            return zweck
    return ('')
