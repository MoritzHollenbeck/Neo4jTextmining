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


def addBranch(restTree, subTree):
    print("this is the restTree" + str(restTree))
    print("this is the subTree " + str(subTree))
    global diseaseDict
    if subTree is None:
        return restTree
    elif restTree is None:
        return subTree
    else:
        #should only be one object at a time since this is the just created subtree
        for element in subTree:
            if isinstance(element, dict):
                for element2 in restTree:
                    if element2 in element:
                        restTree = {element: addBranch(restTree[element], subTree[element])}  
            if element in restTree:
                if isinstance(restTree[element], tuple):
                    return restTree[element] + tuple({element:addBranch(restTree[element], subTree[element])})
                else:
                    restTree = {element:addBranch(restTree[element], subTree[element])}
                    return restTree
            else:
                print("salute")
                #print(tuple(restTree)+tuple(subTree))
                return (restTree, subTree)
                #if isinstance(restTree, tuple):
                #    return tuple(subTree) + restTree
                #else:
                #    return (subTree, restTree)


def expandTree(mainTree, branch):
    for key, value in branch.items():
        if key == "id":
            mainTree["id"] = value
            return
        if key in mainTree:
            expandTree(mainTree[key], branch[key])
        else:
            mainTree[key] = branch[key]

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

#right now i am not covering more than one identifier per node
def appendToMainTree(mainTree, subTree):
    global diseaseDict
    if subTree is None:
        return None
    if mainTree is None:
        return subTree
    else:
        for subTreeElement in subTree:
            print("iterating subTree elements")
            if subTreeElement in mainTree:
                print("found subTree in main Tree")
                for element in mainTree:
                    if isinstance(element, dict):
                        print("we found a dict")
                        return appendToMainTree(element, subTreeElement)
                    else:
                        #TODO this right here is not very type save
                         mainTree[subTreeElement] = (element, appendToMainTree(None, subTreeElement))
                         break
            else:
                mainTree[subTreeElement] = subTree
                return mainTree
            

def findSimiliarity(subTree, tree):
  result = []
  subTreeTemp = subTree.copy()
  while tree is not None and len(subTreeTemp)>0:
    tree = tree.get(subTreeTemp[0])
    if tree is not None:
      result.append(subTreeTemp[0])
    subTreeTemp.pop(0)
  return result


def matchNames(word):
    global foundExact, matchFound, foundSynonym
    diseaseIden = None
    if word in diseaseDict:
        if isinstance(diseaseDict[word], str):
            foundExact +=1
            diseaseIden = diseaseDict[word]
        elif isinstance(diseaseDict[word], int):
            #print(searchQuery[0:diseaseDict[word]])
            word = " ".join(searchQuery[0:diseaseDict[word]+1])
            #word = set(searchQuery[0:diseaseDict[word]+1])
            #for element in synonymDict:
            #if word not in tabooDict:
            if word in synonymDict:
                    #if len(word.difference(set(element.split()))) <= len(element)-2:
                diseaseIden = synonymDict[word]
                foundSynonym +=1
                #else:
                    #tabooDict[word] = True
    if diseaseIden is not None:
        print('AHA. found a match in the diseaseDict: found ' + str(word) + ' in disease ' + str(diseaseIden))
        matchFound = True
    return diseaseIden

def buildResults(drugIdentifier, diseaseIdentifier, indication, diseaseName):
    #print('appending a result to the matchlist')
    if (drugIdentifier, diseaseIdentifier, diseaseName, indication) not in matchList:
        matchList.append((drugIdentifier, diseaseIdentifier, diseaseName, indication))
    return 0


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
            synonyms = [name]
            synonymWords = [name]
            namesAndSynonyms = name
        else:
            synonymWords = synonyms
            namesAndSynonyms = synonyms[:]
            namesAndSynonyms.append(name)
        diseaseInden[identifier] = namesAndSynonyms
        # this is commented out, since its an old approach
        #if synonyms is None:
        #    diseaseDict[name.lower()] = identifier
        #else:
        #    diseaseDict[name.lower()] = identifier
        for element in synonyms:
            element.lower()
            synonymWords = element.split()
            subTree = makeEntry(synonymWords, identifier)
            if len(synonymWords) > 0:
                if synonymWords[0] in diseaseDict:
                    #diseaseDict[synonymWords[0]] = addBranch(diseaseDict, subTree)
                    expandTree(diseaseDict, subTree)
                else:
                    diseaseDict[synonymWords[0]] = subTree
            #appendToMainTree(subTree)
            #findSimiliarity(subTree, diseaseDict)
            #if len(synonymWords) == 1:
            #    diseaseDict[synonymWords[0]] = identifier
            #else:
             #   diseaseDict[synonymWords[0]] = int(len(synonymWords))
              #  synonymWords = " ".join(synonymWords)
               # synonymDict[synonymWords] = identifier



def loadDrugs():
    query = 'MATCH (n:Compound) WHERE EXISTS(n.indication) RETURN n LIMIT 500'
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
            #print('looking for word "' + element + '" in list of diseases')
            diseaseIdentifier = matchNames(element)
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
    #loadDrugs()
    # print(diseaseDict)
    # print(synonymDict)
    print(foundExact)
    print(foundSynonym)
    print("overwritten Entries : " + str(overwrittenEntries))
    print(diseaseDict)
    writeResults()
    testing()


if __name__ == "__main__":
    # execute only if run as a script
    main()


#TODO
#WORK ON TABOODICT, THAT MAKES NO SENSE LIKE THAT
#note down drugs with no match with indication
#implement better search
#ignore diesease knoteen mit it 00000001