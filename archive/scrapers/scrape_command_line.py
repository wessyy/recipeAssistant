import re
from recipe_scrapers import scrape_me  # https://github.com/hhursev/recipe-scrapers

# give the url as a string, it can be url from any site listed below
# url = 'https://www.allrecipes.com/recipe/213262/sweet-and-savory-slow-cooker-pulled-pork/?internalSource=similar_recipe_banner&referringId=139603&referringContentType=recipe&clickId=simslot_2'
url = 'https://www.allrecipes.com/recipe/260895/banana-poppy-seed-pancakes/?internalSource=popular&referringContentType=home%20page&clickId=cardslot%2038'
scrape = scrape_me(url)

print scrape.title() + '\n'
print 'Time: ' + str(scrape.total_time()) + '\n'

print " # INSTRUCTIONS # "
instructions = [i for i in scrape.instructions().split('\n') if i is not '']
for instruction in instructions:
	print instruction

unit_types = dict()
# METRIC (volume, weight)
unit_types['milliliter'] = ['ml','milliliter','millilitre','cc','mL',
							'milliliters','millilitres']
unit_types['liter']      = ['l','liter','litre','L','liters','litres']
unit_types['deciliter']  = ['dl','deciliter','decilitre','dL',
							'deciliters','decilitres']
unit_types['milligram']  = ['mg','milligram','milligramme',
							'milligrams','milligrammes']
unit_types['gram']       = ['g','gram','gramme','grams','grammes']
unit_types['kilogram']   = ['kg','kilogram','kilogramme',
							'kilograms','kilogrammes']
# US CUSTOMARY (volume, weight)
unit_types['drop']         = ['drop','dr','gt','gtt','drops','drs']	
unit_types['smidgen']      = ['smidgen','smdg','smi']
unit_types['pinch']        = ['pinch','pn','pinchs','pinches']
unit_types['dash']         = ['dash','ds','dashes']
unit_types['saltspoon']    = ['saltspoon','scruple','ssp',
							  'saltspoons','scruples','ssps']
unit_types['coffeespoon']  = ['coffeespoon','csp','coffeespoons','csps']
unit_types['fluid dram']   = ['fluid dram','fl.dr','fluid drams','fl.drs']
unit_types['dessertspoon'] = ['dessertspoon','dsp','dssp','dstspn',
							  'dessertspoons','dsps','dssps','dstspns']
unit_types['teaspoon']     = ['teaspoon','t','tsp','teaspoons','tsps']
unit_types['tablespoon']   = ['tablespoon','T','tbl','tbs','tbsp',
							  'tablespoons','tbls','tbsps']
unit_types['fluid ounce']  = ['fluid ounce','fl oz','fluid ounces','fl ozs']
unit_types['wineglass']    = ['wineglass','wgf','wineglasses','wgfs']
unit_types['gill']         = ['gill','teacup','gills','teacups']
unit_types['pottle']       = ['pottle','pot','pottles','pots']
unit_types['cup']          = ['cup','c','cups']
unit_types['pint']         = ['pint','p','pt','fl pt','pints','pts','fl pts']
unit_types['quart']        = ['quart','q','qt','fl qt','quarts','qts','fl qts']
unit_types['gallon']       = ['gallon','g','gal','gallons','gals']
unit_types['pound']        = ['pound','lb','pounds','lbs']
unit_types['ounce']        = ['ounce','oz','ounces','ozs']
# DISTANCE:
unit_types['millimeter'] = ['mm','millimeter','millimetre',
							'millimeters','millimetres']
unit_types['centimeter'] = ['cm','centimeter','centimetre',
							'centimeters','centimetres']
unit_types['inch']       = ['inch','"','inches']
unit_types['foot']       = ['foot','\'','feet']
# ALL ABBREVIATIONS
abbrevs = [abbrev for abbrevs in unit_types.values() for abbrev in abbrevs]

def findParentheticals(string):
	if string.find("(") != -1 and string.find(")") != -1:
		paren = string[string.find("("):string.find(")")+1]
		return paren, removeToken(string, paren)
	return (None, string)


def readableFractions(numer, denom):
	intro = 'a' if int(numer) == 1 else str(numer) + ' '
	fraction = ''
	if denom == 2:
		fraction = 'half'
	elif denom == 3:
		fraction = 'third'
	elif denom == 4:
		fraction = 'fourth'
	elif denom == 5:
		fraction = 'fifth'
	elif denom == 6:
		fraction = 'sixth'
	elif denom == 7:
		fraction = 'seventh'
	elif denom == 8:
		fraction = 'eighth'
	elif denom == 9:
		fraction = 'ninth'
	elif denom == 10:
		fraction = 'tenth'
	plural = 's' if int(numer) != 1 else ''
	return intro + fraction + plural


def transformDigits(digits):
	if len(digits) == 3:
		quantity = digits[0] + ' ' + digits[1] + '/' + digits[2]
		readable = digits[0] + ' and ' + readableFractions(digits[1], digits[2])
		value = float(digits[0]) + (float(digits[1]) / float(digits[2]))
		return quantity, readable, value
	elif len(digits) == 2:
		quantity = digits[0] + '/' + digits[1]
		readable = readableFractions(digits[0], digits[1])
		value = float(digits[0]) / float(digits[1])
		return quantity, readable, value
	elif len(digits) == 1:
		readable = 'a' if int(digits[0]) == 1 else digits[0]
		return digits[0], readable, float(digits[0])
	return None, None, None

def findUnit(quantity, qty_value, string):
	words = string.split()
	unit = None
	if ' ' in quantity:
		unit_loc = words.index(quantity.split()[1]) + 1
		if words[unit_loc] == 'fluid' or words[unit_loc] == 'fl':
			# assumes that finding fluid next to a number will always mean
			# that those two words following the number are the units.
			unit = 'fluid ' + words[unit_loc + 1]
	else:
		unit_loc = words.index(quantity) + 1
	unit = words[unit_loc] if unit is None else unit
	if unit in abbrevs:
		for real, abbrev in unit_types.iteritems():    # for name, age in list.items():  (for Python 3.x)
		    if unit in abbrev:
		        unit = pluralize(qty_value, real)
		return unit, removeToken(removeToken(string, unit), quantity)
	return None, removeToken(string, quantity)

def pluralize(quantity, string):
	if float(quantity) > 1.0:
		if string == 'foot':
			return 'feet'
		return string + 's'
	return string

def removeToken(string, token):
	string = string.replace(token, '')
	return string.strip()

raw_ingredients = []
for ingredient in scrape.ingredients():
	original = ingredient
	paren, ingredient = findParentheticals(ingredient)
	quantity, readable, value = transformDigits(filter(str.isdigit, ingredient))
	unit, ingredient = findUnit(quantity, value, ingredient)
	if unit:
		readable += ' ' + unit + ' ' + ingredient
	else:
		readable += ' ' + ingredient
	if paren:
		readable += ' ' + paren
	raw_ingredients.append([readable, value, unit, ingredient, paren])

print "\n # INGREDIENTS # "
# for ingredient in raw_ingredients:
# 	print ingredient

s = [[str(e) for e in row] for row in raw_ingredients]
lens = [max(map(len, col)) for col in zip(*s)]
fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
table = [fmt.format(*row) for row in s]
print '\n'.join(table)

# print scrape.links()