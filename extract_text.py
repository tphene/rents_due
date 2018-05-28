import os
import re
from nltk.stem import LancasterStemmer

dictionary = open("/Users/neil/workplace/stemmed_dictionary.txt").read().lower()

def clean_doc(doc):
    clean_doc = ''
    for char in doc:
        if ((48<=ord(char)<=57) | (65<=ord(char)<=90) | (97<=ord(char)<=122)):
            clean_doc = clean_doc + char
        elif (ord(char) == 39) | (ord(char) == 45):
            continue
        else:
            char = " "
            clean_doc = clean_doc + char
    clean_doc = re.sub(" +", " ", clean_doc)
    clean_doc = clean_doc.lower()
    return clean_doc


def stem_doc(doc):
    stemmer = LancasterStemmer()
    doc = doc.split(" ")
    doc = [stemmer.stem(word).strip() for word in doc]
    doc = " ".join(doc)
    return doc


raw_files = os.listdir("/Users/neil/workplace/raw_files/")
raw_files_string = "\n".join(raw_files)
with open("/Users/neil/workplace/all_filenames.txt", "w") as f:
    f.write(raw_files_string)

for file in raw_files:
    if file.lower() == ".ds_store":
        continue
    if (file.endswith(".txt")) | (file.endswith(".rtf")):
        f = open("/Users/neil/workplace/raw_files/" + str(file))
        doc = f.read()
        f.close()
        doc = clean_doc(doc)
        doc = stem_doc(doc)

        new_file_name = str(file.split(".")[0])
        new_destination = open("/Users/neil/workplace/clean_files/" + str(file), 'w')
        new_destination.write(doc)
        new_destination.close()


    else:
        try:
            base = str(file.split(".")[0])
        except:
            base = str(file)

        print(base)
        ## convert raw file to tiff
        os.system("convert -density 300 /Users/neil/workplace/raw_files/" + file + " -depth 8 -strip -background white -alpha off " + "/Users/neil/workplace/raw_files/" + base + ".tiff")
        ## convert tiff file to txt
        os.system("tesseract /Users/neil/workplace/raw_files/" + base + ".tiff " + "/Users/neil/workplace/temp/" + base)
        ## open new converted txt file in raw folder
        f = open('/Users/neil/workplace/temp/' + base + ".txt")
        doc = f.read()
        doc = clean_doc(doc)
        doc = stem_doc(doc)


        ## calculate the percentage of words in the document that exist in the dictionary
        count = 0
        for element in doc.split(" "):
            if element in dictionary:
                count += 1

        # calculate the percentage of words in the txt document that are in the dictionary
        pct_real = float(count) / len(doc.split(" "))
        #print(file, ": ", pct_real, "\n", doc, "\n\n\n")
        print(file, ": ", pct_real, "\n\n\n")

        print("BASE", base)
        if pct_real >= 0.00:
            ## move files from raw folder to txt folder
            old_destination = "/Users/neil/workplace/temp/" + base + ".txt"
            new_destination = "/Users/neil/workplace/clean_files/" + base + ".txt"
            os.rename(old_destination, new_destination)
        else:
            ## move files from raw folder to failed folder
            old_destination = "/Users/neil/workplace/temp/" + file
            new_destination = "/Users/neil/workplace/failed_files/" + file
            os.rename(old_destination, new_destination)
        os.remove("/Users/neil/workplace/raw_files/" + base + ".tiff")
