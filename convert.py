import os, re, json, bson, pymongo
from bson import json_util
from pymongo import MongoClient
from dotenv import load_dotenv
from glob import glob
import xmltodict

xml_dir = "DB"
json_dir = "JSON"
json_files = glob(json_dir + "/*.json")
atelier_collection = []

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

                if filename.startswith('atelier'):
                    xml = xml['atelier']['reservations']
                    global atelier_collection
                    atelier_collection = xml
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

def entulhar_reservations_in_atelier_collection():
    print("Parsing reservations...")

    # get the reservations json
    for filename in os.listdir(json_dir):
        if filename.startswith('reservation'):
            with open(os.path.join(json_dir, filename), 'r') as f:
                reservation_json = json.load(f)

                # set the atelier_collection slots to be the reservation slots
                for dia in atelier_collection:
                    if dia['date'] == reservation_json['date']:

                        # create an array of reservations
                        if 'reservations' not in dia:
                            dia['reservations'] = []
                        
                        # add reservation in the atelier_collection as array
                        dia['reservations'].append(reservation_json)

                        # remove date from each reservation
                        reservation_json.pop('date')

                        # if reservation state is 'active', subtract 1 from slots
                        if reservation_json['state'] == 'active':
                            dia['slots'] -= 1
                        
                        # if reservation state is 'cancelled', add 1 to the slots
                        elif reservation_json['state'] == 'cancelled':
                            dia['slots'] += 1

    # save the atelier_collection.json
    with open(os.path.join(json_dir, 'atelier_collection.json'), 'w') as f:
        f.write(json.dumps(atelier_collection, indent=4, default=bson.json_util.default))
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

# main
if __name__ == "__main__":
    convert_xml_to_json()
    entulhar_reservations_in_atelier_collection()
    if import_to_mongodb:
        import_atelier_json_to_mongodb()
