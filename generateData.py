from math import nan
from yattag import Doc, indent
import random

doc, tag, text = Doc().tagtext()

#generate random dates between 1960-01-01 and 2010-12-31
birthDates = []
for i in range(0, 100):
    birthDates.append(str(random.randint(1960, 2010)) + "-" + "0" + str(random.randint(1, 9)) + "-" + str(random.randint(1, 31)))

#generate 10 random names
names = ["John", "Raul", "Pablo", "Juan", "Pedro", "Carlos", "Jorge", "Luis", "Jose", "Ramon"]
    

# make a xml from the xml variable above
with tag('reservation'):
    with tag('id'):
        text('1')
    with tag('date'):
        text(random.choice(birthDates))
    with tag('state'):
        text('Active')
    with tag('family'):
        with tag('familyElement'):
            with tag('name'):
                text(random.choice(names))
            with tag('birthDate'):
                text('1992-06-22')
        with tag('familyElement'):
            with tag('name'):
                text('Maria')
            with tag('birthDate'):
                text('1990-05-24')
        with tag('origin', countryCode='PT'):
            with tag('countryName'):
                text('Portugal')
            with tag('cityName'):
                text('Lisbon')


result = indent(
    doc.getvalue(),
    indentation = ' '*4,
    newline = '\r\n'
)

print(result)