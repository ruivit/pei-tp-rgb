from ctypes.wintypes import PINT
from math import nan
from yattag import Doc, indent
import random, os, re
import requests, time
import sys

doc, tag, text = Doc().tagtext()

#generate random dates between 1960-01-01 and 2010-12-31
birthDates = []
for i in range(0, 100):
    birthDates.append(str(random.randint(1960, 2010)) + "-" + "0" + str(random.randint(1, 9)) + "-" + str(random.randint(1, 31)))

dates = []
#generate random dates between 2022-10-10 and 2022-12-25
for i in range(0, 100):
    dates.append(str(random.randint(2022, 2022)) + "-" + str(random.randint(10, 12)) + "-" + str(random.randint(10, 25)))

#generate random needed data
names = ["John", "Raul", "Pablo", "Juan", "Pedro", "Carlos", "Jorge", "Luis", "Jose", "Ramon"]
countryNames = ["Spain", "France", "Germany", "Italy", "Portugal", "United Kingdom", "United States of America", "Canada", "Mexico", "Brazil"]
cityNames = ["Madrid", "Paris", "Berlin", "Rome", "Lisbon", "London", "New York", "Ottawa", "Mexico City", "Sao Paulo"]
countryCodes = ["ES", "FR", "DE", "IT", "PT", "GB", "USA", "CA", "MX", "BR"]


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
                            text('1992-06-22')
                with tag('f:origin', countryCode=random.choice(countryCodes)):
                    with tag('gd:countryName'):
                        text(random.choice(countryNames))
                    with tag('gd:cityName'):
                        text(random.choice(cityNames))
                with tag('f:reservationDates'):
                    with tag('f:numberOfDays'):
                        text(str(random.randint(1, 5)))
                    for j in range(0, random.randint(1, 5)):
                        with tag('f:preferedDates'):
                            text(random.choice(dates))
    
        # save the xml to a variable
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

def randomCancel():
    url = "http://localhost:8984/cancelreservation?id=" + str(random.randint(1, 100))
    
    time.sleep(0.05)
    response = requests.request("GET", url)
    
    print(response.text)

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
for i in range(1, int(sys.argv[1]+1)):
    createData()

# POST it to BaseX
POSTreservations()

# Cancel some random reservations
for cancel in range(1, int(sys.argv[2]+1)):
    randomCancel()

exportData()