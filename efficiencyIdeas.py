#ideass to make code run faster

#preprocessing
#filter out unused phrases
#  TAGGING: DrugQuest uses the Reflect
# tagging service [13] to identify proteins and chemicals
# and the BeCAS tagging service for diseases/disorders
# and pathways identification. source(DrugQuest - a text mining workflow for
# drug association discovery)
#HAVE TO APPLY TO BE ABLE TO ACCCESS NOT SURE IF WORKS

#build TABOO list -> check for every word if its in the disease database, if not put in list so next search is more efficient


#efficient logic
#use a dictionary tree structure to better search the data. this could be used for the synonyms
