from py2neo import Graph
import csv

g = Graph("http://localhost:7474/db/data/",auth=("neo4j", ""))

#global variables, hopefully i find a better place :)
drugNames = []
diseaseNames = []
diseaseSynonyms = []
identifiers = []
indications = []
diseaseDict = {}
drugDict = {}
matchDict = {}



#zu erklärung : auth=("user_name","")

#hier der Aufruf einer query und wie man die Ergebnisse durchläuft.

query = 'MATCH (n:Disease) RETURN n'
results = g.run(query)


# load in disease names first and the match their names while you load in drug indications
for result, in results:
    name = result['name']
    synonyms = result['synonyms']
    #synonymList = synonyms.split()
    diseaseDict[name] = synonyms

    #diseaseSynonyms.append(synonyms)
    #diseaseSynonyms.append(name)

query = 'MATCH (n:Compound) RETURN n'
#query = 'MATCH (n) WHERE EXISTS(n.name) RETURN DISTINCT "node" as entity, n.name AS name'
#query = 'MATCH (n) WHERE EXISTS(n.identifier) RETURN DISTINCT "node" as entity, n.identifier AS identifier'
results = g.run(query)

for result, in results:
    name = result['name']
    #drugNames.append(name)
    indication = result['indication']
    if indication == None:
        indication = "ThisIsADummyString"
    #print(indication)
    drugDict[name] = indication.split()
    indications.append(indication)
    #identifier = results['identifier']
    #identifiers.append(identifier)



merged_list = [(drugNames[i], diseaseNames[i]) for i in range(0, len(diseaseNames))]

def matchNames():
    for element in drugDict:
        for synonym in element:
            print()
    return 0


with open('finalList.csv', 'w', newline='', encoding="utf-8") as csvfile:
    nameWriter = csv.writer(csvfile, delimiter=' ',  quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for element in merged_list:
        #print(element)
        nameWriter.writerow([element])
#print(drugDict)
