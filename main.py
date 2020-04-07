from py2neo import Graph
import csv
import string

g = Graph("http://localhost:7474/db/data/",auth=("neo4j", ""))

#global variables, hopefully i find a better place for these :)


diseaseDict = {}
drugDict = {}
#matchDict = {}
matchList = []


#zu erklärung : auth=("user_name","")

def matchNames(word):
    diseaseIden = None
    if word in diseaseDict:
        diseaseIden = diseaseDict[word]
        print('AHA. found a match in the diseaseDict: found ' + str(word) + ' in disease ' + str(diseaseIden))
    return diseaseIden

def buildResults(drugIdentifier, diseaseIdentifier):
    print('appending a result to the matchlist')
    matchList.append((drugIdentifier, diseaseIdentifier))
    return 0


#hier der Aufruf einer query und wie man die Ergebnisse durchläuft.

query = 'MATCH (n:Disease) RETURN n'
results = g.run(query)


# load in disease names first and the match their names while you load in drug indications
#beim einlesen direkt .lower benutzen
for result, in results:
    name = result['name']
    identifier = result['identifier']
    synonyms = result['synonyms']
    #synonymDict = {}
    if synonyms == None:
        print('no synonyms found')
        diseaseDict[name] = {identifier}
        #synonymDict[identifier] = {name}
    else:
        for element in synonyms:
            element.lower()
            print('appending synonyms of ' + str(identifier) + ' to dictionary')
            diseaseDict[element] = {identifier}
            #for element in synonyms:
                #synonymWords = element.split()
                #synonymDict[identifier] = {}



query = 'MATCH (n:Compound) WHERE EXISTS(n.indication) RETURN n'
results = g.run(query)

# auch hier lowercase

for result, in results:
    name = result['name']
    identifier = result['identifier']
    indication = result['indication'].lower().translate(str.maketrans('', '', string.punctuation))

    splitIndication = indication.split()
    for element in splitIndication:
        print('looking for word "' + element + '" in list of diseases')
        diseaseIdentifier = matchNames(element)
        if diseaseIdentifier != None:
            buildResults(identifier, diseaseIdentifier)

        #drugDict[identifier] = indication.split()
        #search here

with open('finalList.csv', 'w', newline='', encoding="utf-8") as csvfile:
    nameWriter = csv.writer(csvfile, delimiter=' ',  quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for element in matchList:
        nameWriter.writerow([element])
print(diseaseDict)
