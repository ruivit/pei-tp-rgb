from yattag import Doc, indent
import random, re
import requests, time
import sys, os

# create dates between 1990 and 2010 (younger people)
birthDatesNew = []
for i in range(0, 100):
    birthDatesNew.append(str(random.randint(1990, 2010)) + "-" + str(random.randint(10, 12)) + "-" + str(random.randint(10, 28)))

# create dates between 1960 and 1990 (older people)
birthDatesOld = []
for i in range(0, 100):
    birthDatesOld.append(str(random.randint(1960, 1990)) + "-" + str(random.randint(10, 12)) + "-" + str(random.randint(10, 28)))

infants = []
for i in range(0, 100):
    infants.append(str(random.randint(2012, 2021)) + "-" + str(random.randint(10, 12)) + "-" + str(random.randint(10, 28)))

# create random dates between 2022-10-10 and 2022-12-25 for the reservations
dates = []
for i in range(0, 100):
    dates.append(str(random.randint(2022, 2022)) + "-" + str(random.randint(10, 12)) + "-" + str(random.randint(10, 25)))

# create random needed data
manNames = ["John", "Raul", "Pablo", "Juan", "Pedro", "Carlos", "Jorge", "Luis", "Jose", "Ramon"]
womanNames = ["Maria", "Marta", "Laura", "Sara", "Ana", "Carmen", "Carla", "Pilar", "Sofia", "Martina"]
phoneNumbers = ["911922933", "123123123", "944955966", "900900900", "351234567", "256123456", "912341234"]

# create a two dimensional array with the random generated data of countryNames and Cities
countryNames = ["Spain", "France", "Germany", "Italy", "Portugal", "United Kingdom", "United States of America", "Canada", "Mexico", "Brazil"]
cityNames = ["Madrid", "Paris", "Berlin", "Rome", "Lisbon", "London", "New York", "Ottawa", "Mexico City", "Sao Paulo"]

countryData = []
if (len(countryNames) == len(cityNames)):
    for i in range(0, len(countryNames)):
        countryData.append([])
        countryData[i].append(countryNames[i])
        countryData[i].append(cityNames[i])


# create XMLs with the random generated data (named "reservationX.xml")
def createXMLfiles():
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
                        if (i == int(sys.argv[1])/2):
                            with tag('f:name'):
                                text(manNames[random.randint(0, len(manNames)-1)])
                            with tag("f:sex"):
                                text("Masculine")
                        else:
                            with tag('f:name'):
                                text(womanNames[random.randint(0, len(womanNames)-1)])
                            with tag("f:sex"):
                                text("Feminine")
                        if (i == int(sys.argv[1])/4):
                            with tag('f:birthDate'):
                                text(random.choice(birthDatesOld))
                            if (i == int(sys.argv[1])/2):
                                with tag('f:birthDate'):
                                    text(random.choice(birthDatesNew))
                        else:
                            with tag('f:birthDate'):
                                text(random.choice(infants))
                if (random.randint(1, 4) == 2):
                    with tag('f:emergencyContact'):
                        text(phoneNumbers[random.randint(0, len(phoneNumbers)-1)])
                with tag('f:origin'):
                    rInt = random.randint(1, len(countryData)-1)
                    with tag('gd:countryName'):
                        text(countryData[rInt][0])
                    with tag('gd:cityName'):
                        text(countryData[rInt][1])
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



def deleteResources():
    # delete and create a fresh BaseX DB
    url = "http://localhost:8984/DCDB"
    
    time.sleep(0.05)
    response = requests.request("GET", url)

    # go into the DB folder and remove the files
    try:
        for file in os.listdir(r'.\DB'):
            os.remove(os.path.join(r'.\DB', file))
    except FileNotFoundError:
        print("Creating directory DB...")
        os.makedirs(os.path.join(os.path.dirname(__file__), 'DB'))
        for file in os.listdir(r'.\DB'):
            os.remove(os.path.join(r'.\DB', file))

    # go into the export folder and remove the files
    try:
        for file in os.listdir(r'.\export'):
            os.remove(os.path.join(r'.\export', file))
    except FileNotFoundError:
        print("Creating directory export...")
        os.makedirs(os.path.join(os.path.dirname(__file__), 'export'))
        for file in os.listdir(r'.\export'):
            os.remove(os.path.join(r'.\export', file))


def POSTreservations():
    liveProbe = 0
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
                try:
                    response = requests.request("POST", url, headers=headers, data=content)
                except requests.exceptions.ConnectionError:
                    print("Connection error")
                    liveProbe += 1
                    if (liveProbe == 3):
                        print("\n[!] BaseX seems not to be running [!]\n")
                        sys.exit()


def randomCancel():
# cancel some random reservations indicated by the cli argument
    url = "http://localhost:8984/cancelreservation?id=" + str(random.randint(1, 100))
    
    time.sleep(0.05)
    response = requests.request("GET", url)


def exportData():
# export the database of BaseX
    url = "http://localhost:8984/exportdatabase"
    
    time.sleep(0.05)
    response = requests.request("GET", url)
    

# ------- INIT ------- #
try:
    arg = sys.argv[1]
except IndexError:
    print("""Script Execution:
$ python generateData.py <number> <cancel>
    where <number> is the number of XMLs to create
    and <cancel> is the number of reservations to cancel""")
    exit()

# delete older resources
deleteResources()
print("Deleting old resources...")

# Create XMLs with random data in it
print("Creating XMLs...")
for i in range(1, int(sys.argv[1])):
    createXMLfiles()

# POST it to BaseX
print("POSTing XMLs to BaseX...")
POSTreservations()


# Cancel some random reservations
print("Cancelling reservations...")
try:
    for cancel in range(1, int(sys.argv[2])):
        randomCancel()
except IndexError:
    print("No parameter was given to cancel reservations")
    print("Want to cancel 25% of the reservations? (y/N)")
    if (input() == "y"):
        print("Cancelling 25% of the reservations...")
        for cancel in range(1, int(sys.argv[1])//4):
            randomCancel()

# ask the user if he wants to export the database
try:
    if sys.argv[3]:
        exportData()
    else:
        print("Do you want to export the database? (y/N)")
        if (input() == "y"):
            print("Exporting database...")
            exportData()
            
except IndexError:
    print("Do you want to export the database? (y/N)")
    input = input()
    if (input == "y"):
        print("Exporting database...")
        exportData()
    else:
        print("Database not exported!")
        print("Exiting...")

try:
    if sys.argv[3] == "rui":
        print("Sending data to Mongo...")
        exec(open("convert.py").read())
except IndexError:
    print("No parameter was given to send data to Mongo")