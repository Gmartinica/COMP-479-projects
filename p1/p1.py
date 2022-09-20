import os
import re
from nltk import word_tokenize
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords


def make_directory(path):
    try:
        os.makedirs(path, exist_ok=True)  # Make directory for new files
    except OSError:
        print("ERROR MAKING DIRECTORY " + path)


def get_raw_content(path):
    raw = 'Foo'
    try:
        f = open(path)
        raw = f.read()  # raw text
        f.close()
    except IOError:
        print("Error: File does not exist")
    return raw


def read_files(path, last_index):
    """Reads sgm files from a given directory and writes """
    file_list = [file for file in os.listdir(path) if file.endswith(".sgm")]
    file_list.sort()  # For indexing the first 5 documents
    print(file_list)
    testing_file_list = file_list[:last_index]  # Getting first 5 documents

    directory = "step1files"
    make_directory(directory)

    docs = {}
    for filename in testing_file_list:
        raw = get_raw_content(path + '/' + filename)
        text = re.sub(r'&(.*?)\s|<(.*?)>', '', raw)  # Remove metadata tags and HTML entities
        docs[filename] = text
        try:
            # Write output to new file
            new_file = open(directory + '/' + "altered-" + filename, "w")
            new_file.write(text)
            new_file.close()
        except IOError:
            print("Error: File does not exist")
    return docs


def tokenize(docs):
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


def make_lowercase(docs):
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


def apply_porter_stemmer(docs):
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


def remove_stop_words(docs, word_list):
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
    docs = read_files('./reuters21578', 5)
    docs = tokenize(docs)
    docs = make_lowercase(docs)
    docs = apply_porter_stemmer(docs)
    docs = remove_stop_words(docs, stopwords.words('english'))


if __name__ == "__main__":
    main()
