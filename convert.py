import os, re, json, bson, pymongo
from datetime import datetime
from bson import json_util
from pymongo import MongoClient
from dotenv import load_dotenv
from glob import glob
import xmltodict

#input
xml_dir = "DB"

# output
json_dir = "JSON"

json_files = glob(json_dir + "/*.json")
atelier_collection = []
slots_sanity_check = False

load_dotenv()
import_to_mongodb = os.getenv('IMPORT_TO_MONGODB')
if import_to_mongodb:
    mongodb_host=os.getenv("MONGODB_HOST")
    mongodb_dbname=os.getenv("MONGODB_DBNAME")
    mongodb_user=os.getenv("MONGODB_USER")
    mongodb_password=os.getenv("MONGODB_PASSWORD")

def clean_xml(content):
    # remove the namespaces
    content = re.sub('xmlns(|:xsi|:f)="http.+(?=">)"', '', content)
    # remove the prefixes
    content = re.sub('(f:)|(gd:)', '', content)
    # remove the whitespaces
    content = re.sub('(?=\s>)\s', '', content)
    return content

def convert_xml_to_json():
    print("Converting XML to JSON...")
    for filename in os.listdir(xml_dir):
        # get only the xml files
        if not filename.endswith ('.xml'):
            continue
        with open(os.path.join(xml_dir, filename), 'r') as f:
            content = clean_xml(f.read())
            # save as json
            with open(os.path.join(json_dir, filename.replace('.xml', '.json')), 'w') as f:
                xml = xmltodict.parse(content)

                if filename.startswith('atelier'):
                    xml = xml['atelier']['reservations']
                    global atelier_collection
                    atelier_collection = xml
                    
                    if slots_sanity_check:
                        # set all atelier_json slots to be the default 50
                        for dia in atelier_collection:
                            dia['slots'] = 50

                elif filename.startswith('reservation'):
                    xml = xml['reservation']
                    # se for array, transforma em dict
                    if isinstance(xml['family']['familyElement'], dict):
                        xml['family']['familyElement'] = [xml['family']['familyElement']]

                f.write(json.dumps(xml, indent=4, default=bson.json_util.default))
    print("Conversion complete!")

def create_more_mongodb_data(dia):
    if 'active_reservations' not in dia:
        dia['active_reservations'] = 0
    if 'canceled_reservations' not in dia:
        dia['canceled_reservations'] = 0
    if 'people_in_active_reservations' not in dia:
        dia['people_in_active_reservations'] = 0
    if 'people_in_canceled_reservations' not in dia:
        dia['people_in_canceled_reservations'] = 0

def entulhate_more_mongodb_data(dia, reservation_json):
    if reservation_json['state'] == 'Active':
        # add 'active_reservations' to the atelier_collection
        dia['active_reservations'] += 1
        
        # add 'people_in_active_reservations' to the people_in_active_reservations
        dia['people_in_active_reservations'] += int(reservation_json['family']['numberElements'])

    elif reservation_json['state'] == 'Canceled':
        # add 'canceled_reservations' to the atelier_collection
        dia['canceled_reservations'] += 1

        # add 'people_in_canceled_reservations' to the people_in_canceled_reservations
        dia['people_in_canceled_reservations'] += int(reservation_json['family']['numberElements'])

    # for each each familyElement
    for familyElement in reservation_json['family']['familyElement']:
        if 'age' not in familyElement:
            birth_day = familyElement['birthDate']
            reservation_date = dia['date']

            # remove '-' from the dates
            birth_day = birth_day.replace('-', '')
            reservation_date = reservation_date.replace('-', '')

            familyElement['age_when_visiting'] = (int(reservation_date) - int(birth_day)) // 10000
    return reservation_json

def fix_atelier_data_types(atelier_collection):
    for dia in atelier_collection:
        # mantem ambos date e date_obj porque nao da import bem para mongodb
        dia['date_obj'] = datetime.strptime(dia['date'], '%Y-%m-%d')
        dia['slots'] = int(dia['slots'])

def fix_reservation_data_types(reservation_json):
    # convert id to int
    reservation_json['id'] = int(reservation_json['id'])
    
    # convert 'date' to datetime - num da
    for family_element in reservation_json['family']['familyElement']:
        family_element['birthDate_obj'] = datetime.today().replace(microsecond=0)
    
    # convert numberElements to int
    reservation_json['family']['numberElements'] = int(reservation_json['family']['numberElements'])

def entulhar_reservations_in_atelier_collection():
    print("Parsing reservations...")

    # get the reservations json
    for filename in os.listdir(json_dir):
        # get only the json files
        if not filename.endswith ('.json'):
            continue
        if filename.startswith('reservation'):
            with open(os.path.join(json_dir, filename), 'r') as f:
                reservation_json = json.load(f)

                # set the atelier_collection slots to be the reservation slots
                for dia in atelier_collection:

                    # create the 'more_mongodb_data' fields
                    create_more_mongodb_data(dia)
                    
                    if dia['date'] == reservation_json['date']:
                        # create an array of reservations
                        if 'reservations' not in dia:
                            dia['reservations'] = []
                        
                        # add reservation in the atelier_collection as array
                        dia['reservations'].append(reservation_json)

                        # remove date from each reservation
                        reservation_json.pop('date')
                        
                        # add data to the 'more_mongodb_data' fields
                        reservation_json = entulhate_more_mongodb_data(dia, reservation_json)

                        if slots_sanity_check:
                            # if reservation state is 'Active', subtract 1 from slots
                            if reservation_json['state'] == 'Active':
                                dia['slots'] -= 1
                        break

                fix_reservation_data_types(reservation_json)
    fix_atelier_data_types(atelier_collection)

    # save the atelier_collection.json
    with open(os.path.join(json_dir, 'atelier_collection.json'), 'w') as f:
        f.write(json.dumps((atelier_collection), indent=4, default=bson.json_util.default))
    print("Parsing complete!")

def get_mongodb():
    client = MongoClient(mongodb_host, username=mongodb_user, password=mongodb_password)
    return client[mongodb_dbname]
    
def import_atelier_json_to_mongodb():
    print("Importing atelier_collection.json to MongoDB...")
    with open(os.path.join(json_dir, 'atelier_collection.json'), 'r') as f:
        atelier_collection_json = json.load(f)

    collection_dst = 'atelier'
    mymongodb = get_mongodb()[collection_dst]

    print("Overriding collection...")
    mymongodb.drop()
    mymongodb.insert_many(atelier_collection_json)
    print("Import complete!")

    print("Indexing...")
    index_info=mymongodb.index_information()
    if 'date_1' not in index_info:
        mymongodb.create_index([('date', pymongo.ASCENDING)], unique=True)
    print("Indexing complete!")

# join all reservations into an array of reservations and save it in the reservations.json
def join_reservations_json():
    print("Joining reservations...")
    reservations_json = []
    for filename in os.listdir(json_dir):
        # get only the json files
        if not filename.endswith ('.json'):
            continue
        if filename.startswith('reservation'):
            with open(os.path.join(json_dir, filename), 'r') as f:
                reservation_json = json.load(f)
                reservations_json.append(reservation_json)
    with open(os.path.join(json_dir, 'all_reservations.json'), 'w') as f:
        f.write(json.dumps(reservations_json, indent=4, default=bson.json_util.default))
    print("Joining complete!")
    return reservations_json

def import_reservations_json_to_mongodb(reservations_json):
    print("Importing reservations.json to MongoDB...")
    collection_dst = 'reservations'
    mymongodb = get_mongodb()[collection_dst]

    print("Overriding collection...")
    mymongodb.drop()
    mymongodb.insert_many(reservations_json)
    print("Import complete!")

    print("Indexing...")
    index_info=mymongodb.index_information()
    if 'id_1' not in index_info:
        mymongodb.create_index([('id', pymongo.ASCENDING)], unique=True)
    print("Indexing complete!")

# main
if __name__ == "__main__":
    convert_xml_to_json()
    entulhar_reservations_in_atelier_collection()
    if import_to_mongodb:
        import_atelier_json_to_mongodb()
        reservations_json = join_reservations_json()
        import_reservations_json_to_mongodb(reservations_json)
