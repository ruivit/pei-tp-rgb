import os, re, json, bson, pymongo
from bson import json_util
from pymongo import MongoClient
from dotenv import load_dotenv
from glob import glob
import xmltodict

xml_dir = "DB"
json_dir = "JSON"
json_files = glob(json_dir + "/*.json")
workshop_collection = []

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
        with open(os.path.join(xml_dir, filename), 'r') as f:
            content = clean_xml(f.read())
            # save as json
            with open(os.path.join(json_dir, filename.replace('.xml', '.json')), 'w') as f:
                xml = xmltodict.parse(content)

                if filename.startswith('workshop'):
                    xml = xml['workshop']['reservations']
                    global workshop_collection
                    workshop_collection = xml
                    # set all workshop_json slots to be the default 50
                    for dia in workshop_collection:
                        dia['slots'] = 50

                elif filename.startswith('reservation'):
                    xml = xml['reservation']
                    # se for array, transforma em dict
                    if isinstance(xml['family']['familyElement'], dict):
                        xml['family']['familyElement'] = [xml['family']['familyElement']]

                f.write(json.dumps(xml, indent=4, default=bson.json_util.default))
    print("Conversion complete!")

def entulhar_reservations_in_workshop_collection():
    print("Parsing reservations...")

    # get the reservations json
    for filename in os.listdir(json_dir):
        if filename.startswith('reservation'):
            with open(os.path.join(json_dir, filename), 'r') as f:
                reservation_json = json.load(f)

                # set the workshop_collection slots to be the reservation slots
                for dia in workshop_collection:
                    if dia['date'] == reservation_json['date']:

                        # create an array of reservations
                        if 'reservations' not in dia:
                            dia['reservations'] = []
                        
                        # add reservation in the workshop_collection as array
                        dia['reservations'].append(reservation_json)

                        # remove date from each reservation
                        reservation_json.pop('date')

                        # remove 1 from slots for each reservation
                        dia['slots'] -= 1
                        break

    # save the workshop_collection.json
    with open(os.path.join(json_dir, 'workshop_collection.json'), 'w') as f:
        f.write(json.dumps(workshop_collection, indent=4, default=bson.json_util.default))
    print("Parsing complete!")

def get_mongodb():
    client = MongoClient(mongodb_host, username=mongodb_user, password=mongodb_password)
    return client[mongodb_dbname]
    
def import_workshop_json_to_mongodb():
    print("Importing workshop_collection.json to MongoDB...")
    with open(os.path.join(json_dir, 'workshop_collection.json'), 'r') as f:
        workshop_collection_json = json.load(f)

    collection_dst = 'workshop'
    mymongodb = get_mongodb()[collection_dst]

    print("Overriding collection...")
    mymongodb.drop()
    mymongodb.insert_many(workshop_collection_json)
    print("Import complete!")

    print("Indexing...")
    index_info=mymongodb.index_information()
    if 'date_1' not in index_info:
        mymongodb.create_index([('date', pymongo.ASCENDING)], unique=True)
    print("Indexing complete!")

# main
if __name__ == "__main__":
    convert_xml_to_json()
    entulhar_reservations_in_workshop_collection()
    if import_to_mongodb:
        import_workshop_json_to_mongodb()
