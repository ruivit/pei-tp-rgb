import re
import xmljson

# 1. Remover os namespaces do que esta na DB, office e reservations
# 2. Usar regex para remover os namespaces
# 3. Deixar os namespaces...

regex = '{http.+(?=})}'

file = r"C:\Program Files (x86)\BaseX\webapp\DB\reservation1.xml"

# convert the file to json
#with open(file, 'r') as f:
#    content = f.read()
#    content = xmljson.yahoo.(content)
#    print(content)

with open(file, 'r') as f:
    content = f.read()
    content = re.sub(regex, '', content)
    print(content)
