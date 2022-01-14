from ctypes.wintypes import PINT
from math import nan
from yattag import Doc, indent
import random, os, re
import requests, time
import sys

doc, tag, text = Doc().tagtext()

# create dates between 1990 and 2010 (younger people)
birthDatesNew = []
for i in range(0, 100):
    birthDatesNew.append(str(random.randint(1990, 2010)) + "-" + str(random.randint(10, 28)) + "-" + str(random.randint(10, 28)))

# create dates between 1960 and 1990 (older people)
birthDatesOld = []
for i in range(0, 100):
    birthDatesOld.append(str(random.randint(1960, 1990)) + "-" + str(random.randint(10, 28)) + "-" + str(random.randint(10, 28)))

# create random dates between 2022-10-10 and 2022-12-25 for the reservations
dates = []
for i in range(0, 100):
    dates.append(str(random.randint(2022, 2022)) + "-" + str(random.randint(10, 12)) + "-" + str(random.randint(10, 25)))

# create random needed data
names = ["John", "Raul", "Pablo", "Juan", "Pedro", "Carlos", "Jorge", "Luis", "Jose", "Ramon"]
countryNames = ["Spain", "France", "Germany", "Italy", "Portugal", "United Kingdom", "United States of America", "Canada", "Mexico", "Brazil"]
cityNames = ["Madrid", "Paris", "Berlin", "Rome", "Lisbon", "London", "New York", "Ottawa", "Mexico City", "Sao Paulo"]
countryCodes = ["ES", "FR", "DE", "IT", "PT", "GB", "USA", "CA", "MX", "BR"]


# create XMLs with the random generated data (named "reservationX.xml")
def createData():
    with open(os.path.join(os.path.dirname(__file__), 'export', 'reservation' + str(i) + '.xml'), 'w') as f:
        f.write(makeXML(i))

def makeXML(i):
    # make a empty xml
    doc, tag, text = Doc().tagtext()

    # make a root tag
    with tag('root'):
        with tag('reservation'):
            with tag('f:family'):
                # create a random number of familyElement
                for j in range(0, random.randint(1, 7)):
                    with tag('f:familyElement'):
                        with tag('f:name'):
                            text(random.choice(names))
                        with tag('f:birthDate'):
                            text(random.choice(birthDatesOld))
                with tag('f:origin', countryCode=random.choice(countryCodes)):
                    with tag('gd:countryName'):
                        text(random.choice(countryNames))
                    with tag('gd:cityName'):
                        text(random.choice(cityNames))
                # create a random number of reservationDates
                with tag('f:reservationDates'):
                    with tag('f:numberOfDays'):
                        text(str(random.randint(1, 5)))
                    for j in range(0, random.randint(1, 5)):
                        with tag('f:preferedDates'):
                            text(random.choice(dates))
    
        # save the xml to a variable and return it
        xml = indent(doc.getvalue())
        return xml

def POSTreservations():
    regex = '<reservation>'
    regex2 = """<?xml version="1.0" encoding="UTF-8"?>
    <reservation   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"  
                    xmlns="http://www.atelierRGB.pt/Reservation" 
                    xsi:schemaLocation="http://www.atelierRGB.pt/Reservation ../XSD/Reservation.xsd"
                    
                    xmlns:f="http://www.atelierRGB.pt/Family"
                    xmlns:gd="http://www.atelierRGB.pt/GeographicData">"""

    # loop through the reservation files and POST it to BaseX
    for filename in os.listdir(r'C:\Program Files (x86)\BaseX\webapp\export'):
        if filename.startswith('reservation'):
            with open(os.path.join(r'C:\Program Files (x86)\BaseX\webapp\export', filename), 'r') as f:
                
                content = f.read()

                content = re.sub(regex, regex2, content)

                url = "http://localhost:8984/makereservation"

                headers = {
                'Authorization': 'Basic YWRtaW46YWRtaW4=',
                'Content-Type': 'application/xml'
                }

                time.sleep(0.05)
                response = requests.request("POST", url, headers=headers, data=content)

                print(response.text)

# cancel some random reservations indicated by the cli argument
def randomCancel():
    url = "http://localhost:8984/cancelreservation?id=" + str(random.randint(1, 100))
    
    time.sleep(0.05)
    response = requests.request("GET", url)
    
    print(response.text)

# export the database of BaseX
def exportData():
    url = "http://localhost:8984/exportdatabase"
    
    response = requests.request("GET", url)
    
    print(response.text)

# ------- INIT ------- #
try:
    arg = sys.argv[1]
except IndexError:
    print("""Script Execution:
$ python generateData.py <number> <cancel>
    where <number> is the number of XMLs to create
    and <cancel> is the number of reservations to cancel""")
    exit()

# Create XMLs with random data in it
for i in range(1, int(sys.argv[1])):
    createData()

# POST it to BaseX
POSTreservations()

# Cancel some random reservations
for cancel in range(1, int(sys.argv[2])):
    randomCancel()

#exportData()