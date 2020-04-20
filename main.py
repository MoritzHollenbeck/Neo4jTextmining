from py2neo import Graph
import csv
import string


g = Graph("http://localhost:7474/db/data/",auth=("neo4j", ""))

#global variables, hopefully i find a better place for these :)

synonymDict = {}
diseaseDict = {}
drugDict = {}
#matchDict = {}
matchList = []
searchQuery = []
lonelyDrug = []
longSearch = False
matchFound = False


#zu erklärung : auth=("user_name","")

def matchNames(word):
    diseaseIden = None
    if word in diseaseDict:
        if isinstance(diseaseDict[word], str):
            diseaseIden = diseaseDict[word]
        elif isinstance(diseaseDict[word], int):
            print(searchQuery[0:diseaseDict[word]])
            #word = " ".join(searchQuery[0:diseaseDict[word]+1])
            word = set(searchQuery[0:diseaseDict[word]+1])
            for element in synonymDict:
                #if word in synonymDict:
                if len(word.difference(set(element.split()))) <= len(element)-2:
                    diseaseIden = synonymDict[element]
    if diseaseIden is not None:
        print('AHA. found a match in the diseaseDict: found ' + str(word) + ' in disease ' + str(diseaseIden))
        matchFound = True
    return diseaseIden

def buildResults(drugIdentifier, diseaseIdentifier):
    print('appending a result to the matchlist')
    if (drugIdentifier, diseaseIdentifier) not in matchList:
        matchList.append((drugIdentifier, diseaseIdentifier))
    return 0


#hier der Aufruf einer query und wie man die Ergebnisse durchläuft.

query = 'MATCH (n:Disease) RETURN n'
results = g.run(query)


# load in disease names first and the match their names while you load in drug indications

for result, in results:
    name = result['name']
    identifier = result['identifier']
    synonyms = result['synonyms']

    if synonyms == None:
        #print('no synonyms found')
        diseaseDict[name] = {identifier}

    else:
        #for element in synonyms:
         #   element.lower()
          #  print('appending synonyms of ' + str(identifier) + ' to dictionary')
            # right here i am trying to build a dict which contains others dicts corresponding to the synonym words
           # diseaseDict[element] = {identifier}
        for element in synonyms:
            diseaseDict[name] = {identifier}
            element.lower()
            synonymWords = element.split()
            if len(synonymWords) == 1:
                diseaseDict[synonymWords[0]] = {identifier}
            else:
                diseaseDict[synonymWords[0]] = int(len(synonymWords))
                synonymWords = " ".join(synonymWords)
                synonymDict[synonymWords] = identifier



query = 'MATCH (n:Compound) WHERE EXISTS(n.indication) RETURN n'
results = g.run(query)


for result, in results:
    matchFound = False
    name = result['name']
    identifier = result['identifier']
    indication = result['indication'].lower().translate(str.maketrans('', '', string.punctuation))

    splitIndication = indication.split()
    wordCount = 0
    for element in splitIndication:
        wordCount += 1
        searchQuery = splitIndication[:wordCount]
        print('looking for word "' + element + '" in list of diseases')
        diseaseIdentifier = matchNames(element)
        if diseaseIdentifier is not None:
            buildResults(identifier, diseaseIdentifier)
    if not matchFound:
        lonelyDrug.append(identifier)
        #drugDict[identifier] = indication.split()
        #search here


with open('finalList.csv', 'w', newline='', encoding="utf-8") as csvfile:
    nameWriter = csv.writer(csvfile, delimiter=' ',  quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for element in matchList:
        nameWriter.writerow([element])

with open('lonelyDrugs.csv', 'w', newline='', encoding="utf-8") as csvfile:
    nameWriter = csv.writer(csvfile, delimiter=' ',  quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for element in lonelyDrug:
        nameWriter.writerow([element])

print(diseaseDict)
print(synonymDict)

#TODO
#note down drugs with no match
#implement better search