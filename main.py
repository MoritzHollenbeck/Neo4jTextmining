from py2neo import Graph
import csv
import string


g = Graph("http://localhost:11003/db/data/",auth=("neo4j", ""))

#global variables, hopefully i find a better place for these :)

synonymDict = {}
diseaseDict = {}
diseaseInden = {}
drugDict = {}
#matchDict = {}
tabooDict = {}
matchList = []
searchQuery = []
lonelyDrug = []
longSearch = False
matchFound = False
foundExact = 0
foundSynonym = 0
overwrittenEntries = 0
foundId = 0
errorCount = 0
lastId = None

def makeEntry(rest, indentifier):
  if len(rest) == 0:
      return rest
  elif len(rest) == 1:
      idenDict = {}
      idenDict["id"] = indentifier
      rest = {rest[0]: idenDict}
      return rest
  else:
      first_value = rest[0]
      rest = {first_value: makeEntry(rest[1:], indentifier)}
      return rest



def findDisease(searchQuery, mainTree):
    global foundId, errorCount, matchFound, lastId
    # soft tissue sarcoma in
    if "id" in mainTree:
        # print("nice we found the following id: " + mainTree["id"])
        matchFound = True
        foundId += 1
        lastId = mainTree["id"]
        word = searchQuery[0]
        if len(searchQuery) == 0:
            return mainTree["id"]
        if word in mainTree:
            return findDisease(searchQuery, mainTree[word])
        else:
            return mainTree["id"]
    elif len(searchQuery) == 0 or searchQuery[0] not in mainTree:
        if lastId is not None:
            return lastId
        else:
            return
    elif "id" not in mainTree:
        word = searchQuery[0]
        try:
            searchQuery.pop(0)
        except AttributeError:
            errorCount+=1
            print("ERROR"+searchQuery)
        if len(searchQuery) == 0:
           if "id" in mainTree[word]:
               foundId += 1
               matchFound = True
               return mainTree[word]["id"]
        #print("we found the word °" + word + "° in the tree")
        return findDisease(searchQuery, mainTree[word])
    # I think this will fall a part
    else:
        #print("nice we found the following id: " + mainTree["id"])
        matchFound = True
        foundId+=1
        return mainTree["id"]


def expandTree(mainTree, branch):
    for key, value in branch.items():
        if key == "id":
            mainTree["id"] = value
            return
        if key in mainTree:
            expandTree(mainTree[key], branch[key])
        else:
            mainTree[key] = branch[key]

def searching(sentence, mainTree):
    ids = []
    wordCount = 0
    for element in sentence:
        query = sentence[wordCount:]
        ids.append(findDisease(query, mainTree))
        wordCount+=1
    return ids

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
    #print('appending a result to the matchlist')
    if (drugIdentifier, diseaseIdentifier, diseaseName, indication) not in matchList:
        matchList.append((drugIdentifier, diseaseIdentifier, diseaseName, indication))
    return 0


def cleanSynonyms(synonyms):
    removeList = []
    cleanList = []
    for element in synonyms:
           if element != "EXACT" and element[0] != '[' and element != "Id" and element != "id" and element != "ID":
            cleanList.append(element.lower())
    return cleanList


def loadDiseases():
    #hier der Aufruf einer query und wie man die Ergebnisse durchläuft.
    global overwrittenEntries
    query = 'MATCH (n:Disease) RETURN n'
    results = g.run(query)

    for result, in results:
        name = result['name']
        identifier = result['identifier']
        synonyms = result['synonyms']
        if synonyms is None:
            if name is not None:
                synonyms = [name.lower()]
            else:
                synonyms = [name]
            synonymWords = [name]
            namesAndSynonyms = name
        else:
            synonymWords = synonyms
            namesAndSynonyms = synonyms[:]
            if name is not None:
                namesAndSynonyms.append(name.lower())
        diseaseInden[identifier] = namesAndSynonyms
        for element in namesAndSynonyms:
            synonymWords = element.split()
            synonymWords = cleanSynonyms(synonymWords)
            subTree = makeEntry(synonymWords, identifier)
            #if identifier == "MONDO:0001657":
            #    print(subTree)
            #print(synonymWords)
            #print(subTree)
            if len(synonymWords) > 0:
                if synonymWords[0] in diseaseDict:
                    #diseaseDict[synonymWords[0]] = addBranch(diseaseDict, subTree)
                    expandTree(diseaseDict, subTree)
                else:
                    diseaseDict[synonymWords[0]] = subTree[synonymWords[0]]



def loadDrugs():
    global searchQuery, matchFound
    # {identifier:"DB05374"}; {identifier:"DB05109"}
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
            searchQuery = splitIndication[wordCount:]
            #print('looking for word "' + element + '" in list of diseases')
            #diseaseIdentifier = matchNames(element)
            #print(searchQuery)
            diseaseIdentifier = findDisease(searchQuery, diseaseDict)
            #print(diseaseIdentifier)
            if diseaseIdentifier is not None:
                buildResults(identifier, diseaseIdentifier, indication, diseaseInden[diseaseIdentifier])
        if not matchFound:
            lonelyDrug.append((identifier, indication))
            #drugDict[identifier] = indication.split()

def writeResults():
    with open('finalList.csv', 'w', newline='', encoding="utf-8") as csvfile:
        nameWriter = csv.writer(csvfile, delimiter=' ',  quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for element in matchList:
            nameWriter.writerow([element])

    with open('lonelyDrugs.csv', 'w', newline='', encoding="utf-8") as csvfile:
        nameWriter = csv.writer(csvfile, delimiter=' ',  quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for element in lonelyDrug:
            nameWriter.writerow([element])



def main():
    loadDiseases()
    loadDrugs()
    print(diseaseDict["soft"]['tissue']['sarcoma'])
    # print(diseaseDict["brain"])
    # print(synonymDict)
    print(foundExact)
    print(foundSynonym)
    print("overwritten Entries : " + str(overwrittenEntries))
    writeResults()
    #testing()
    print(findDisease(["Obesity"], diseaseDict))
    #print(cleanSynonyms(["What", "is", "UP"]))
    print(foundId)
    print(errorCount)


if __name__ == "__main__":
    # execute only if run as a script
    main()


#TODO
#WORK ON TABOODICT, THAT MAKES NO SENSE LIKE THAT
#note down drugs with no match with indication
#implement better search
#ignore diesease knoteen mit it 00000001