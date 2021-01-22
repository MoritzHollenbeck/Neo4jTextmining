from py2neo import Graph
import csv
import string
import copy

#database location may vary
g = Graph("http://localhost:11003/db/data/",auth=("neo4j", ""))
#g = Graph("http://localhost:7474/db/data/", auth=("neo4j", "test"))



diseaseDict = {}
diseaseInden = {}
drugDict = {}
tabooDict = {}
matchList = []
searchQuery = []
lonelyDrug = []
matchFound = False
foundId = 0
errorCount = 0
lastId = None
searchDepth = 0


#function in which a branch is made from a synonym
def makeEntry(rest, indentifier):
  #termination
  if len(rest) == 0:
      return rest
  #last element with id added
  elif len(rest) == 1:
      idenDict = {}
      idenDict["id"] = indentifier
      rest = {rest[0]: idenDict}
      return rest
  #adding depth
  else:
      first_value = rest[0]
      rest = {first_value: makeEntry(rest[1:], indentifier)}
      return rest


#searchfunction given a query and the searchtree
def findDisease(searchQuery, mainTree):
    global foundId, errorCount, matchFound, lastId, searchDepth
    #counting searchdepth
    searchDepth+=1
    #case if the current location contains matching id
    if "id" in mainTree:
        matchFound = True
        foundId += 1
        lastId = mainTree["id"]
        word = searchQuery[0]
        #termination with current id
        if len(searchQuery) == 0:
            splitIndication[searchDepth:]
            return mainTree["id"]
        #continue searching for longer match
        if word in mainTree:
            return findDisease(searchQuery, mainTree[word])
        #no other match can be found so current id is returned
        else:
            splitIndication[searchDepth:]
            return mainTree["id"]
    #no more mach can be found or the query is empty
    elif len(searchQuery) == 0 or searchQuery[0] not in mainTree:
        #last found id is returned
        if lastId is not None:
            matchFound = True
            splitIndication[searchDepth:]
            return lastId
        #sadly no id is returned / lonely Drug
        else:
            return
    #id cannot be found but the searchquery isnt empty
    elif "id" not in mainTree:
        word = searchQuery[0]
        try:
            #remove last searched word from query
            searchQuery.pop(0)
        except AttributeError:
            errorCount+=1
        #check if query is empty now
        if len(searchQuery) == 0:
           # case if id is found
           if "id" in mainTree[word]:
               splitIndication[searchDepth:]
               foundId += 1
               matchFound = True
               return mainTree[word]["id"]
        #recursion occurs if the maintree contains the latest element in the query
        return findDisease(searchQuery, mainTree[word])
    else:
        matchFound = True
        foundId+=1
        return mainTree["id"]

#branch is added to the tree
def expandTree(mainTree, branch):
    for key, value in branch.items():
        #adding a leaf inside the tree
        if key == "id":
            mainTree["id"] = value
            return
        #recusively exploring partial congruence of treee and branch
        if key in mainTree:
            expandTree(mainTree[key], branch[key])
        #branching off
        else:
            mainTree[key] = branch[key]

#help function for the tests
def searching(sentence, mainTree):
    ids = []
    wordCount = 0
    for element in sentence:
        query = sentence[wordCount:]
        ids.append(findDisease(query, mainTree))
        wordCount+=1
    return ids

#testfunction
def testing():
    mainTree = {}
    testList1 = ["lets", "test", "that"]
    testSubTree1 = (makeEntry(testList1, "1"))
    print(testSubTree1)
    testList2 = ["lets", "test"]
    testSubTree2 = (makeEntry(testList2, "2"))
    print(testSubTree2)
    testList3 = ["lets", "test", "this"]
    testSubTree3 = (makeEntry(testList3, "3"))
    print(testSubTree3)
    testList4 = ["lets", "test", "another","thing"]
    testSubTree4 = (makeEntry(testList4, "4"))
    print(testSubTree4)
    expandTree(mainTree, testSubTree1)
    print("MAINTREE", mainTree)
    expandTree(mainTree, testSubTree2)
    print("MAINTREE", mainTree)
    expandTree(mainTree, testSubTree3)
    print("MAINTREE", mainTree)
    expandTree(mainTree, testSubTree4)
    print("MAINTREE", mainTree)
    testSentence1 = ["lets", "test", "this"]
    testSentence2 = ["lets", "test", "this", "and"]
    testSentence3 = ["lets","find"]
    print(searching(testSentence1, mainTree))





def buildResults(drugIdentifier, diseaseIdentifier, indication, diseaseName):
    if (drugIdentifier, diseaseIdentifier, diseaseName, indication) not in matchList:
        matchList.append((drugIdentifier, diseaseIdentifier, diseaseName, indication))
    return 0

#removing problematic elemts from a string
def cleanSynonyms(synonyms):
    cleanList = synonyms
    for element in synonyms:
           if element == "EXACT" or element[0] == '[' or element == "Id" or element == "id" or element == "ID" or\
            element == "AS EXACT []":
            cleanList = ["THIS SYNONYM WAS DELETED"]
    return cleanList


# the diseases are loaded with identifier. name and synonyms
def loadDiseases():
    query = 'MATCH (n:Disease) RETURN n.identifier, n.name, n.synonyms '
    results = g.run(query)

    counter=0
    for identifier, name, synonyms, in results:
        counter+=1
        if identifier=="MONDO:0005154":
            print('huhu')
        # some diseases have no synonyms
        if synonyms is None:
            namesAndSynonyms = name
        else:
            synonymWords = synonyms
            namesAndSynonyms = [x.rsplit(' [')[0] for x in synonyms]
            if name is not None:
                namesAndSynonyms.append(name.lower())
        diseaseInden[identifier] = namesAndSynonyms
        for element in namesAndSynonyms:
            synonymWords = element.split()
            #remove certain elements for the synonyms
            synonymWords = cleanSynonyms(synonymWords)
            #if identifier == 'MONDO:0004978':
            #    print(synonymWords)
            #a simgular branch for the searchtree is made
            subTree = makeEntry(synonymWords, identifier)
            if len(synonymWords) > 0:
                if synonymWords[0] in diseaseDict:
                    #branch appended to tree
                    expandTree(diseaseDict, subTree)
                else:
                    diseaseDict[synonymWords[0]] = subTree[synonymWords[0]]
    print(counter)


#the drugs with identifier, name and indication are loaded
def loadDrugs():
    global searchQuery, matchFound, searchDepth, splitIndication, lastId
    #neo4j query to return all components for which an indication exists
    query = 'MATCH (n:Compound) WHERE EXISTS(n.indication) RETURN n'
    results = g.run(query)
    #the depth in which the description of the drug is searched in the tree
    searchDepth = 0

    count=0
    for result, in results:
        count+=1
        matchFound = False
        lastId = None
        name = result['name']
        identifier = result['identifier']
        #the indication is put in lowercase and the punctuation is altered
        indication = result['indication'].lower().translate(str.maketrans('', '', string.punctuation))
        splitIndication = indication.split()
        #as long as there are elemnts in the indication the search continues
        while len(splitIndication)>0:
            splitIndication.pop(0)
            searchList = copy.deepcopy(splitIndication)
            diseaseIdentifier = findDisease(searchList, diseaseDict)
            #if a matching disease is found a result will be returned
            keyExists = diseaseInden.get(diseaseIdentifier)
            if matchFound and keyExists:
                splitIndication = splitIndication[searchDepth:]
                buildResults(identifier, diseaseIdentifier, indication, diseaseInden[diseaseIdentifier])
        if not matchFound:
            lonelyDrug.append((identifier, indication))
    print(count)


def writeResults():
    #file for the results
    with open('finalList.csv', 'w', newline='', encoding="utf-8") as csvfile:
        nameWriter = csv.writer(csvfile, delimiter='\t',  quotechar='"', quoting=csv.QUOTE_MINIMAL)
        nameWriter.writerow(["DRUG IDENTIFIER","DISEASE IDENTIFIER", "DISEASE SYNONYMES","DRUG DESCRIPTION"])
        for element in matchList:
            nameWriter.writerow(list(element))
    #file for the drugs for which no match was found
    with open('lonelyDrugs.csv', 'w', newline='', encoding="utf-8") as csvfile:
        nameWriter = csv.writer(csvfile, delimiter='\t',  quotechar='"', quoting=csv.QUOTE_MINIMAL)
        nameWriter.writerow(["IDENTIFIER","DRUG DESCRIPTION"])
        for element in lonelyDrug:
            nameWriter.writerow(list(element))



def main():
    loadDiseases()
    loadDrugs()
    writeResults()
    print(lonelyDrug)

    print(diseaseDict["asthma"]["id"])
    #print(diseaseDict["insomnia"]["id"])
    #print(diseaseDict["respiratory"]["infection"]["id"])
    #print(diseaseDict)
    # print(diseaseDict["thrombosis"]["id"])
    #print[diseaseDict["cystic"]["fibrosis"]["id"]]
    # print(diseaseDict["hepatitis"]["id"])
    # print(diseaseDict["osteoporosis"]["id"])

    print(str(foundId)+" diseases were found in the database")


if __name__ == "__main__":
    # execute only if run as a script
    main()
