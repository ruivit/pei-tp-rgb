from urllib import response
from yattag import Doc, indent
import random, re
import requests
import sys, os
import datetime

# create dates between 1990 and 2020
birthDatesNew = []
for i in range(0, 100):
    birthDatesNew.append(datetime.date(random.randint(1990, 2020), random.randint(1, 12), random.randint(1, 28)).strftime('%Y-%m-%d'))
    

# create dates between 1960 and 1990 (older people)
birthDatesOld = []
for i in range(0, 100):
    birthDatesOld.append(datetime.date(random.randint(1960, 1990), random.randint(1, 12), random.randint(1, 28)).strftime('%Y-%m-%d'))

# create dates between 2012 and 2021 (infants)
infants = []
for i in range(0, 100):
    infants.append(datetime.date(random.randint(2000, 2020), random.randint(1, 12), random.randint(1, 28)).strftime('%Y-%m-%d'))

# create random dates between 2022-09-15 and 2022-12-23 for the reservations
dates = []
for i in range(0, 100):
    for j in range(0, random.randint(1, 5)):
        dates.append(datetime.datetime(2022, random.randint(9, 12), random.randint(1, 23)).strftime('%Y-%m-%d'))

# create random names for the family elements
manNames = ["John", "Raul", "Pablo", "Juan", "Pedro", "Carlos", "Jorge", "Luis", "Jose", "Ramon"]
womanNames = ["Maria", "Marta", "Laura", "Sara", "Ana", "Carmen", "Carla", "Pilar", "Sofia", "Martina"]

# create random phone numbers
phoneNumbers = ["911922933", "123123123", "944955966", "900900900", "351234567", "256123456", "912341234"]

# create country and city data
countryNames = ["Spain", "France", "Germany", "Italy", "Portugal", "United Kingdom", "United States of America", "Canada", "Brazil"]
cityNames = [["Madrid", "Toledo", "Badajoz"], ["Paris", "Lyon", "Marseille"], ["Berlin", "Munich", "Frankfurt"],["Rome", "Milan", "Venice"], ["Lisbon", "Porto", "Funchal"], ["London", "Manchester", "Liverpool"],["New York", "Los Angeles", "Chicago"], ["Toronto", "Vancouver", "Montreal"], ["Brasilia", "Rio de Janeiro", "Sao Paulo"]]

# join the country and city data in one array
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
                # create a random number of familyElements
                for j in range(0, random.randint(1, 7)):
                    with tag('f:familyElement'):
                        # half being men and the other half being woman
                        if (random.randint(1, 2) == 1):
                            with tag('f:name'):
                                text(manNames[random.randint(0, len(manNames)-1)])
                        else:
                            with tag('f:name'):
                                text(womanNames[random.randint(0, len(womanNames)-1)])
                        
                        # have 50% chance of at least 1 being a grown up
                        # have 25% change of being a older person 
                        # and 25% being an infant
                        if (random.randint(1, 2) == 1):
                            with tag('f:birthDate'):
                                text(birthDatesNew[random.randint(0, len(birthDatesNew)-1)])
                        elif (random.randint(1, 3) == 1):
                            with tag('f:birthDate'):
                                text(birthDatesOld[random.randint(0, len(birthDatesOld)-1)])
                        else:
                            with tag('f:birthDate'):
                                text(infants[random.randint(0, len(infants)-1)])

                with tag('f:emergencyContact'):
                    text(phoneNumbers[random.randint(0, len(phoneNumbers)-1)])
                with tag('f:origin'):
                    rInt = random.randint(1, len(countryData)-1)
                    with tag('gd:countryName'):
                        text(countryData[rInt][0])
                    with tag('gd:cityName'):
                        text(countryData[rInt][1][random.randint(0, len(countryData[rInt][1])-1)])

                # create a random number of reservationDates
                with tag('f:reservationDates'):
                    numberOfDays = random.randint(1, 5)
                    with tag('f:numberOfDays'):
                        text(str(numberOfDays))
                    for j in range(0, numberOfDays):
                        with tag('f:preferedDates'):
                            text(random.choice(dates))
    
        # save the xml to a variable and return it
        xml = indent(doc.getvalue())
        return xml



def deleteResources():
    # delete and create a fresh BaseX DB
    url = "http://localhost:8984/DCDB"
    
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

    # go into JSON folder and remove the files
    try:
        for file in os.listdir(r'.\JSON'):
            os.remove(os.path.join(r'.\JSON', file))
    except FileNotFoundError:
        print("Creating directory JSON...")
        os.makedirs(os.path.join(os.path.dirname(__file__), 'JSON'))
        for file in os.listdir(r'.\JSON'):
            os.remove(os.path.join(r'.\JSON', file))

def POSTreservations():
    regex = '<reservation>'
    regex2 = """<?xml version="1.0" encoding="UTF-8"?>
    <reservation   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"  
                    xmlns="http://www.atelierRGB.pt/Reservation" 
                    xsi:schemaLocation="http://www.atelierRGB.pt/Reservation ../XSD/Reservation.xsd"
                    
                    xmlns:f="http://www.atelierRGB.pt/Family"
                    xmlns:gd="http://www.atelierRGB.pt/GeographicData">"""

    # loop through the reservation files and POST it to BaseX
    for filename in os.listdir(r'.\export'):
        if filename.startswith('reservation'):
            with open(os.path.join(r'.\export', filename), 'r') as f:
                
                content = f.read()

                # remove the namespaces and prefixes
                content = re.sub(regex, regex2, content)

                url = "http://localhost:8984/makereservation"

                headers = {
                'Authorization': 'Basic YWRtaW46YWRtaW4=',
                'Content-Type': 'application/xml'
                }

                # POST the xml to BaseX
                try:
                    response = requests.request("POST", url, headers=headers, data=content)
                except requests.exceptions.ConnectionError:
                    print("\n[!] BaseX seems not to be running [!]\n")
                    sys.exit()


def randomCancel():
# cancel some random reservations indicated by the cli argument
    url = "http://localhost:8984/cancelreservation?id=" + str(random.randint(1, int(sys.argv[1])))
    
    response = requests.request("GET", url)


def exportData():
# export the database of BaseX to export directory
    url = "http://localhost:8984/exportdatabase"
    
    response = requests.request("GET", url)
    

def initialChecks():
    # check if the current directory is webapp
    if 'webapp' not in os.getcwd():
        print("\n[!] Please run this script from the webapp directory [!]\n")
        sys.exit()

    # check if the DB and export directories exist
    try:
        for file in os.listdir(r'.\DB'):
            os.remove(os.path.join(r'.\DB', file))
    except FileNotFoundError:
        print("DB directory was not found\nCreating it...")
        os.makedirs(os.path.join(os.path.dirname(__file__), 'DB'))
        
    try:
        for file in os.listdir(r'.\export'):
            os.remove(os.path.join(r'.\export', file))
    except FileNotFoundError:
        print("export directory was not found\nCreating it...")
        os.makedirs(os.path.join(os.path.dirname(__file__), 'export'))


    # send a GET request to the BaseX webpage to check if it is running
    url = "http://localhost:8984/"
    try:
        response = requests.request("GET", url)
    except requests.exceptions.ConnectionError:
        print("\n[!] BaseX seems not to be running [!]\n")
        sys.exit()

    


# ------- INIT ------- #
if __name__ == "__main__":
    try:
        arg = sys.argv[1]
    except IndexError:
        print("""Script Execution:
$ python generateData.py <number> <cancel> "sendmongo" 
    <number> is the number of XMLs to create
    <cancel> is the number of reservations to cancel (optional)
    sendmongo is the option to run the convert.py script and send data to mongoDB (optional)""")
        sys.exit()
    
    # do some initial checks
    initialChecks()

    # delete older resources
    deleteResources()
    print("Deleting old resources...")

    # Create XMLs with random data in it
    print("Creating XMLs...")
    for i in range(1, int(sys.argv[1])):
        createXMLfiles()

    # POST it to BaseX
    eta = (int(sys.argv[1]) * 45) / 1000
    eta = round(eta / 60)
    print("POSTing XMLs to BaseX... (ETA: " + str(eta) + " minutes)")
    POSTreservations()

    # Cancel some random reservations
    eta = (int(sys.argv[1]) * 45) / 1000
    eta = round(eta / 60)
    print("Cancelling reservations... (ETA: " + str(eta) + " minutes)")
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
    # only if the user didnt specify that he wants to send the data to mongoDB
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
        if sys.argv[3] == "sendmongo":
            print("Running script convert.py...")
            exec(open("convert.py").read())
    except IndexError:
        print("No parameter was given to send data to Mongo")