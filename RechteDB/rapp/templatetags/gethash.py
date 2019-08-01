from django import template
from urllib.parse import quote, unquote

register = template.Library()

# Liefert einen Wert eines Hashes für die Templates
@register.filter
def hash(h, key):
	if key in h:
		return h[key]
	return h

# Liefert einen Wert eines 2-teiligen Hashes für die Templates
@register.filter
def hash2(_1, _2):
	return _1, _2

@register.filter
def hash3(_1_2, _3):
	_1, _2 = _1_2
	key = '!'.join((_2, _3))
	return hash(_1, key)

@register.filter
def part1(_1):
	s = _1.split("!")
	if len(s) > 1:
		return s[0]
	else:
		return s

@register.filter
def part1a(_1):
	s = part1(_1)
	if len(s) > 0:
		return quote(part1(_1)[0], safe='')
	else:
		return ""

@register.filter
def part2(_1):
	s = _1.split("!")
	if len(s) > 1:
		return s[1]
	else:
		return "Kein zweites Element gefunden"

# Liefert den Zweck einer Rolle (ist der zweite Teil des Tupels)
@register.filter
def finde(inputset, search):
	for s in inputset:
		(name, zweck) = s
		if name == search:
			return zweck
	return ('')

@register.filter
def sort(menge):
	liste = list(menge)
	liste.sort()
	return liste

@register.filter
def vergleich(einzel, menge):
	for element in menge:
		if element == einzel:
			print ('gefunden:', element, einzel)
			return True
	return False