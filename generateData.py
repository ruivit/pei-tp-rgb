from ctypes.wintypes import PINT
from math import nan
from yattag import Doc, indent
import random, os

doc, tag, text = Doc().tagtext()

#generate random dates between 1960-01-01 and 2010-12-31
birthDates = []
for i in range(0, 100):
    birthDates.append(str(random.randint(1960, 2010)) + "-" + "0" + str(random.randint(1, 9)) + "-" + str(random.randint(1, 31)))

dates = []
#generate random dates between 2022-10-10 and 2022-12-25
for i in range(0, 100):
    dates.append(str(random.randint(2022, 2022)) + "-" + str(random.randint(10, 12)) + "-" + str(random.randint(10, 25)))

#generate 10 random names
names = ["John", "Raul", "Pablo", "Juan", "Pedro", "Carlos", "Jorge", "Luis", "Jose", "Ramon"]

countryNames = ["Spain", "France", "Germany", "Italy", "Portugal", "United Kingdom", "United States of America", "Canada", "Mexico", "Brazil"]

cityNames = ["Madrid", "Paris", "Berlin", "Rome", "Lisbon", "London", "New York", "Ottawa", "Mexico City", "Sao Paulo"]

countryCodes = ["ES", "FR", "DE", "IT", "PT", "GB", "USA", "CA", "MX", "BR"]

# make a xml from the xml variable above


def makeXML(i):
    # make a empty xml
    doc, tag, text = Doc().tagtext()

    # make a root tag
    with tag('root'):
        with tag('reservation'):
            with tag('f:family'):
                with tag('f:familyElement'):
                    with tag('f:name'):
                        text(random.choice(names))
                    with tag('f:birthDate'):
                        text('1992-06-22')
                with tag('f:familyElement'):
                    with tag('f:name'):
                        text(random.choice(names))
                    with tag('f:birthDate'):
                        text('1990-05-24')
                with tag('f:origin', countryCode=random.choice(countryCodes)):
                    with tag('gd:countryName'):
                        text(random.choice(countryNames))
                    with tag('gd:cityName'):
                        text(random.choice(cityNames))
                with tag('f:reservationDates'):
                    with tag('f:numberOfDays'):
                        text(str(random.randint(1, 5)))
                    with tag('f:preferedDates'):
                        text(random.choice(dates))
                    with tag('f:preferedDates'):
                        text(random.choice(dates))
    
        # save the xml to a variable
        xml = indent(doc.getvalue())
        return xml

for i in range(1, 101):
    # save the xml to a file in dir export
    with open(os.path.join(os.path.dirname(__file__), 'export', 'reservation' + str(i) + '.xml'), 'w') as f:
        f.write(makeXML(i))
