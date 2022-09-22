import os
import re
from nltk import word_tokenize
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords


def make_directory(path: str):
    """Makes directory with the given path. Name included in path"""
    try:
        os.makedirs(path, exist_ok=True)  # Make directory for new files
    except OSError:
        print("ERROR MAKING DIRECTORY " + path)


def get_text_content(path: str) -> str:
    """Gets the text of each article. Reads file line by line up until <BODY> tag found, appends all the contents of the
    article's body up until it finds the word 'reuter' which is used to end each article. Does this until EOF"""
    text = ''
    currently_searching = True
    try:
        with open(path, 'rt') as file:
            for line in file:
                if currently_searching:
                    line_index = line.find("<BODY>")
                    body_found = True if line_index > -1 else False  # True if body tag found
                    if body_found:
                        currently_searching = False
                        text_to_add = line[line_index + 6:]
                        text += text_to_add
                else:
                    if line.lower().find(" reuter") > -1:
                        currently_searching = True
                    else:
                        text += line
        file.close()
    except IOError:
        print("Error: File does not exist")
    return text


def read_files(path: str, last_index: int) -> dict:
    """Reads sgm files from a given directory and removes metadata. Returns a dict with the form
    {document: text}"""
    file_list = [file for file in os.listdir(path) if file.endswith(".sgm")]
    file_list.sort()  # For indexing the first 5 documents
    testing_file_list = file_list[:last_index]  # Getting first 5 documents

    directory = "step1files"
    make_directory(directory)

    docs = {}
    for filename in testing_file_list:
        text = get_text_content(path + '/' + filename)
        docs[filename] = text
        try:
            # Write output to new file
            new_file = open(directory + '/' + "altered-" + filename, "w")
            new_file.write(text)
            new_file.close()
        except IOError:
            print("Error: File does not exist")
    return docs


def tokenize(docs: dict) -> dict:
    """Given a dict with {document: text}, tokenizes each element"""
    directory = "step2files"
    make_directory(directory)
    for filename in docs:
        docs[filename] = word_tokenize(docs[filename])
        # Write output to new file
        new_file = open(directory + '/' + "altered-" + filename, "w")
        for word in docs[filename]:
            new_file.write(word + '\n')
        new_file.close()
    return docs


def make_lowercase(docs: dict) -> dict:
    """Given a dict with {document: text}, makes all values of the dict lowercase"""
    directory = "step3files"
    make_directory(directory)
    for filename in docs:
        lower_case = [w.lower() for w in docs[filename]]
        docs[filename] = lower_case
        # Write output to new file
        new_file = open(directory + '/' + "altered-" + filename, "w")
        for word in docs[filename]:
            new_file.write(word + '\n')
        new_file.close()
    return docs


def apply_porter_stemmer(docs: dict) -> dict:
    """Given a dict with {document: text}, apply Porter Stemmer algorithm"""
    directory = "step4files"
    make_directory(directory)

    porter = PorterStemmer()

    for filename in docs:
        docs[filename] = [porter.stem(token) for token in docs[filename]]
        new_file = open(directory + '/' + "altered-" + filename, "w")
        for word in docs[filename]:
            new_file.write(word + '\n')
        new_file.close()
    return docs


def remove_stop_words(docs: dict, word_list: list) -> dict:
    """Given a dict with {document: text} and a list of stop words, remove the stop words from text"""
    directory = "step5files"
    make_directory(directory)
    for filename in docs:
        docs[filename] = [w for w in docs[filename] if w not in word_list]
        new_file = open(directory + '/' + "altered-" + filename, "w")
        for word in docs[filename]:
            new_file.write(word + '\n')
        new_file.close()
    return docs


def main():
    path = "./reuters21578"
    last_index = 5
    stop_words_list = stopwords.words('english')
    docs = read_files(path, last_index)
    docs = tokenize(docs)
    docs = make_lowercase(docs)
    docs = apply_porter_stemmer(docs)
    docs = remove_stop_words(docs, stop_words_list)


if __name__ == "__main__":
    main()
