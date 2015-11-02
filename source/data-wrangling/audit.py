"""
Your task in this exercise has two steps:

- audit the OSMFILE and change the variable 'mapping' to reflect the changes needed to fix 
    the unexpected street types to the appropriate ones in the expected list.
    You have to add mappings only for the actual problems you find in this OSMFILE,
    not a generalized solution, since that may and will depend on the particular area you are auditing.
- write the update_name function, to actually fix the street name.
    The function takes a string with street name as an argument and should return the fixed name
    We have provided a simple test so that you see what exactly is expected
"""
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import operator

OSMFILE = "sample.osm"

# General auditing of street names to find oddities
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
street_type_re_as_part = re.compile(r'\S+\.?$', re.IGNORECASE)
part_of = re.compile(r'(stra\xdfe|br\xfccke|weg|allee|ring|steig|platz|stieg|steg|aue|acker|heide|feld|lauf|kamp|blick|burg|schlag|wald|tal|tor|eck|sprung|reihe|plantage|graben|hain|heck|horst|mark|rain|schanze|gang|wall|hof|grund|anger|plan|ufer|passage|zeile|hang|winkel|garten|park|wiese|berg|damm|pfad|gasse|promenade)$', re.IGNORECASE)
prefix = re.compile(r'^(Am|Zum|Zur|An der|Im|Zu den|Unter den|An den|Zwischen den|Hinter den|In den|Auf dem|Weg am|Allee der|Rue|Avenue|Alt-|Via|Stra\xdfe)', re.IGNORECASE)

expected = ["Weg", u'Stra\xdfe', "Damm", "Platz", "Allee", "Gang", "Garten", "Anger",
            "Ring", "Steg", "Steig", "Pfad", "Promenade", "See", "Siedlung", "Zeile", "Winkel", "Weinberg", "Ufer",
            "Aue", "Bahn", "Berg", "Chaussee", "Feld", "Bogen", "Aue", "Esplanade", "G\xe4rten", "Heide", "Karree", "Kehre"]

# Performs a general auditing of the street names to find oddities
# This was my starting point
def audit_street_type(street_types, street_name):
    m = part_of.search(street_name)
    if m:
        return
    m = prefix.match(street_name)
    if m:
        return
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

# Finds the most commonly used keys for ways and nodes to see which ones might
# be interesting for further analysis
def getKeys(osmfile):
    osm_file = open(osmfile, "r")
    node_keys = {}
    way_keys = {}
    suburb = defaultdict(int)

    for event, elem in ET.iterparse(osm_file, events=("start",)):
         in_de = False
         if elem.tag == "way" or elem.tag == "node":
            for tag in elem.iter("tag"):
                if (tag.attrib['k'] == 'addr:country' and tag.attrib['v'] == 'DE'):
                    in_de = True
            if in_de:
                for tag in elem.iter("tag"):
                    if ((tag.attrib['k'] == 'addr:postcode') and int(tag.attrib['v']) in range(10115, 15000)) or (tag.attrib['k'] != 'addr:postcode'):
                        in_de = True
                    else:
                        in_de = False

            if in_de:
                if elem.tag == "node":
                    for tag in elem.iter("tag"):
                        if tag.attrib['k'] in node_keys:
                            node_keys[tag.attrib['k']] += 1
                        else:
                            node_keys[tag.attrib['k']] = 1
                        if tag.attrib['k'] == 'phone':
                            suburb[tag.attrib['v']] += 1

                if elem.tag == "way":
                    for tag in elem.iter("tag"):
                        if tag.attrib['k'] in way_keys:
                            way_keys[tag.attrib['k']] += 1
                        else:
                            way_keys[tag.attrib['k']] = 1

    return (node_keys, way_keys)


####################################################################
# Work with the findings from the general analysis above:
# 1) misspelled street names (Chaussee)
# 2) inconsistent phone numbers
# 3) inconsistent house numbers

wrong_spelling = re.compile(r'(Chausee|Chausse($|\b))')

# Phone number regexes
v_plus_49 = re.compile(r'\+49([0-9]+)')
v_00490 = re.compile(r'00490([0-9]+)')
v_plus_490 = re.compile(r'\+490([0-9]+)')
v_0049 = re.compile(r'0049([0-9]+)')
v_49 = re.compile(r'49([1-9][0-9]+)')
v_0 = re.compile(r'0([0-9]+)')
v_ex_phone = re.compile(r'\s*Telefon[^0-9+]*(\+*[0-9]+)')


# Correct misspelled street names
def find_misspelled(osmfile):
    osm_file = open(osmfile, "r")
    misspelled = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
         if elem.tag == "way" or elem.tag == "node":
             for tag in elem.iter("tag"):
                if is_street_name(tag):
                    m = wrong_spelling.search(tag.attrib['v'])
                    if m:
                        misspelled[m.group()].add(tag.attrib['v'])
    return misspelled

# Update Misspelled street names
def update_name(name):
    m = wrong_spelling.search(name)
    if m:
        name = wrong_spelling.sub('Chaussee', name)
    return name

# Audit the different ways of specifying phone numbers
def audit_phone(osmfile):
    osm_file = open(osmfile, "r")
    number_type = defaultdict(int)
    phonenumbers = []
    for event, elem in ET.iterparse(osm_file, events=("start",)):
         if elem.tag == "way" or elem.tag == "node":
             for tag in elem.iter("tag"):
                if tag.attrib['k'] == 'phone':
                    phonenumber = tag.attrib['v']
                    phonenumbers.append(phonenumber)
                    phonenumber = phonenumber.replace(' ','')
                    phonenumber = phonenumber.replace('(0)','')
                    phonenumber = phonenumber.replace('(','')
                    phonenumber = phonenumber.replace(')','')
                    phonenumber = phonenumber.replace('-','')
                    phonenumber = phonenumber.replace('/','')
                    phonenumber = phonenumber.replace('+49+49','+49')
                    if re.match('\+49(30|33|34|35|800|180)[0-9]+', phonenumber):
                        number_type['+4930'] += 1
                    elif re.match('0049(30|33|34|35|800|180)[0-9]+', phonenumber):
                        number_type['004930'] += 1
                    elif re.match('49(30|33|34|35|800|180)[0-9]+', phonenumber):
                        number_type['4930'] += 1
                    elif re.match('0(30|33|34|35|800|180)[0-9]+', phonenumber):
                        number_type['030'] += 1
                    elif re.match('\+490(30|33|34|35|800|180)[0-9]+', phonenumber):
                        number_type['+49030'] += 1
                    elif re.match('\+49(17|15|16)[0-9]+', phonenumber):
                        number_type['mobile_+49'] += 1
                    elif re.match('0049(15|17|16)[0-9]+', phonenumber):
                        number_type['mobile0049'] += 1
                    elif re.match('0(17|15|16)[0-9]+', phonenumber):
                        number_type['mobile'] += 1
                    else:
                        number_type[phonenumber] += 1
                        #print elem.tag
                        #for t in elem.iter('tag'):
                        #    print (t.attrib['k'], t.attrib['v'])

    print sorted(number_type.items(), key=operator.itemgetter(1), reverse=True)
    return phonenumbers

# Transform/Correct phone numbers to conform to the following pattern: +49[actual number without leading zero of the prefix]
def update_phonenumber(phonenumber):
    # strip all blanks
    phonenumber = phonenumber.replace(' ', '')
    phonenumber = phonenumber.replace('(0)', '')
    phonenumber = phonenumber.replace('(', '')
    phonenumber = phonenumber.replace(')', '')
    phonenumber = phonenumber.replace('-', '')
    phonenumber = phonenumber.replace('/', '')
    phonenumber = phonenumber.replace('+49+49', '+49')
    m = v_ex_phone.match(phonenumber)
    if m:
        phonenumber = m.group(1)

    regexes = [v_00490, v_0049, v_plus_490, v_49, v_0]
    result = ['+49' + regex.match(phonenumber).group(1) for regex in regexes if regex.match(phonenumber)]
    if result:
        return result[0]
    elif v_plus_49.match(phonenumber):
        return phonenumber
    else:
        return []

# Check the tranformed phone numbers
def check_phone(phonenumbers):
    number_type = defaultdict(int)
    for phonenumber in phonenumbers:
        if not phonenumber:
            continue
        if re.match('\+49[^0][0-9]+', phonenumber):
            number_type['+49_PATTERN'] += 1
        elif re.match('0049(30|33|34|35|800|180|17|15|16)[0-9]+', phonenumber):
            number_type['0049_PATTERN'] += 1
        elif re.match('49(30|33|34|35|800|180|17|15|16)[0-9]+', phonenumber):
            number_type['ERROR'] += 1
            print ("ERROR", phonenumber)
        elif re.match('0(30|33|34|35|800|180|17|15|16)[0-9]+', phonenumber):
            number_type['no_country'] += 1
        elif re.match('\+490(30|33|34|35|800|180|17|15|16)[0-9]+', phonenumber):
            number_type['ERROR'] += 1
            print ("ERROR", phonenumber)
        else:
            number_type[phonenumber] += 1
            #print elem.tag
            # for t in elem.iter('tag'):
            #    print (t.attrib['k'], t.attrib['v'])
    print sorted(number_type.items(), key=operator.itemgetter(1), reverse=True)

# Audit the different ways of specifying house numbers
def audit_housenumber(osmfile):
    osm_file = open(osmfile, "r")
    number_type = defaultdict(int)
    housenumbers = []
    for event, elem in ET.iterparse(osm_file, events=("start",)):
         if elem.tag == "way" or elem.tag == "node":
             for tag in elem.iter("tag"):
                if tag.attrib['k'] == 'addr:housenumber':
                    housenumber = tag.attrib['v']
                    housenumbers.append(housenumber)
                    housenumber = housenumber.replace(' ','')
                    if re.match('[0-9]+$', housenumber):
                        number_type['no_letter'] += 1
                    elif re.match('[0-9]+[a-z]+', housenumber):
                        number_type['small_letter'] += 1
                    elif re.match('[0-9]+[A-Z]+', housenumber):
                        number_type['big_letter'] += 1
                    elif re.match('[0-9]+\-[0-9]+', housenumber):
                        number_type['hyphen'] += 1
                    elif re.match('[0-9]+\/[0-9]+', housenumber):
                         number_type['slash'] += 1
                        #print elem.tag
                        #for t in elem.iter('tag'):
                        #    print (t.attrib['k'], t.attrib['v'])

                    elif re.match('[0-9]+\,[0-9]+', housenumber):
                        number_type['comma'] += 1
                    elif re.match('[0-9]+\;[0-9]+', housenumber):
                        number_type['semicolon'] += 1

                    else:
                        number_type[housenumber] += 1
                        #print elem.tag
                        #for t in elem.iter('tag'):
                        #    print (t.attrib['k'], t.attrib['v'])

    print sorted(number_type.items(), key=operator.itemgetter(1), reverse=True)
    return housenumbers


# Transform the house numbers to a common pattern:
def update_housenumber(housenumber):
    # strip all blanks and make all letters lower case
    housenumber = housenumber.replace(' ','')
    housenumber = housenumber.upper()
    # transform string lists to actual lists in python
    housenumber = housenumber.replace(';',',')
    housenumber = housenumber.replace('+',',')
    # hyphens: transform e.g. 4-6 into [4,5,6]
    m = re.match(r'([0-9]+)\-([0-9]+)', housenumber)
    if m:
        housenumber = range(int(m.group(1)),int(m.group(2))+1)
        housenumber = [str(i) for i in housenumber]
        return housenumber
    if not re.match(r'([A-Z][0-9]+|[0-9]+($|[A-Z]|[-/,][0-9]+\s*))', housenumber):
        #print housenumber
        return []
    # make a python list out of the strings containing a comma-separated list
    if ',' in housenumber:
        return re.split(r',', housenumber)
    else:
        return [housenumber]

# Check the tranformed house numbers
def check_housenumber(housenumbers):
    number_type = defaultdict(int)
    for number in housenumbers:
        for n in number:
            if re.match('[0-9]+$', n):
                number_type['no_letter'] += 1
            elif re.match('[0-9]+[a-z]+', n):
                number_type['small_letter'] += 1
            elif re.match('[0-9]+[A-Z]+', n):
                number_type['big_letter'] += 1
            elif re.match('[0-9]+\-[0-9]+', n):
                number_type['hyphen'] += 1
            elif re.match('[0-9]+\/[0-9]+', n):
                number_type['slash'] += 1
            elif re.match('[0-9]+\,[0-9]+', n):
                number_type['comma'] += 1
            elif re.match('[0-9]+\;[0-9]+', n):
                number_type['semicolon'] += 1

            else:
                number_type[n] += 1
    print sorted(number_type.items(), key=operator.itemgetter(1), reverse=True)


def test():

    # Testing just some regular expressions
    street_name = 'seestra\xdfe'
    assert part_of.search(street_name).group() == 'stra\xdfe'
    street_name = 'seeweg'
    assert part_of.search(street_name).group() == 'weg'
    street_name = 'see'
    assert part_of.search(street_name) == None
    street_name = 'An der Havelspitze'
    assert prefix.match(street_name).group() == 'An der'

    street_name = 'Xyz Chausse'
    assert wrong_spelling.search(street_name).group() == 'Chausse'
    street_name = 'Xyz Chausee'
    assert wrong_spelling.search(street_name).group() == 'Chausee'
    street_name = 'Xyz Chaussee'
    assert wrong_spelling.search(street_name) is None

    housenumber = '248'
    assert re.match('[0-9]+', housenumber) != None
    housenumber = '248g'
    assert re.match(r'[0-9]+[a-z]+', housenumber) != None

    # Run audit, transformation and transformation validation for housenumbers
    numbers = audit_housenumber(OSMFILE)
    numbers_updated = []
    for n in numbers:
        numbers_updated.append(update_housenumber(n))
    check_housenumber(numbers_updated)

    # Run audit, transformation and transformation validation for phonenumbers
    numbers = audit_phone(OSMFILE)
    numbers_updated = []
    for n in numbers:
        numbers_updated.append(update_phonenumber(n))
    check_phone(numbers_updated)

    # Run audit and transformation for misspelled street names
    misspelled = find_misspelled(OSMFILE)
    for st_type, ways in misspelled.iteritems():
        for name in ways:
            better_name = update_name(name)
            print name, "=>", better_name


if __name__ == '__main__':
    test()