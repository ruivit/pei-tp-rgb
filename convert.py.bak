import re, os, json, xmltodict
from pymongo import MongoClient
import pymongo
from pymongo import MongoClient

dir = r"PEITP"

def convert_xml_to_json():

    for filename in os.listdir(dir):
        with open(os.path.join(dir, filename), 'r') as f:
            content = f.read()

            # remove the namespaces
            content = re.sub('xmlns(|:xsi|:f)="http.+(?=">)"', '', content)

            # remove the prefixes
            content = re.sub('(f:)|(gd:)', '', content)

            # remove the whitespaces
            content = re.sub('(?=\s>)\s', '', content)

            # replace the file and save it
            with open(os.path.join(dir, filename), 'w') as f:
                #new_name = filename.replace(".xml", ".json")
                f.write(json.dumps(xmltodict.parse(content)))
                f.close()
            
def get_database():
    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING = "mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false"

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    client = MongoClient(CONNECTION_STRING)

    # Create the database for our example (we will use the same database throughout the tutorial
    return client['basex']
    
# This is added so that many files can reuse the function get_database()
if __name__ == "__main__":    
    convert_xml_to_json()

    dbname = get_database()

    # go trough the json files
    for filename in os.listdir(dir):
        with open(os.path.join(dir, filename), 'r') as f:
            content = f.read()

            # convert the content to a dictionary
            content = json.loads(content)

            dbname.basex.insert_one(content)