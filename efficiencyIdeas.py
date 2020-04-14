#ideass to make code run faster

#preprocessing
#filter out unused phrases
#  TAGGING: DrugQuest uses the Reflect
# tagging service [13] to identify proteins and chemicals
# and the BeCAS tagging service for diseases/disorders
# and pathways identification. source(DrugQuest - a text mining workflow for
# drug association discovery)
#HAVE TO APPLY TO BE ABLE TO ACCESS NOT SURE IF WORKS

#guck dir noch genauer die indications an, vielleicht gibts da satzstrukturen


#build TABOO list -> check for every word if its in the disease database, if not put in list so next search is more efficient


#efficient logic
#use a dictionary tree structure to better search the data. this could be used for the synonyms




#IDEA FOR STRUCTURE

#could be efficient, to save two discionaries for the disease. one is for single words, and the other is for phrases. if you mathc with the single word dict - cool. if you match with the first word of a phrases, you will now extend your search query by the amount of words in the synomynm