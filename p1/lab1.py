from nltk.book import *
from nltk.corpus import reuters

# a
print(len(reuters.fileids()))

# b and #c
total_sentences = 0
total_words = 0
for doc in reuters.fileids():
    total_sentences += len(reuters.words(doc))
    total_words += len(reuters.sents(doc))
print(f'Total words: {total_words}')
print(f'Total sentences: {total_sentences}')

# d
words9920 = reuters.words('training/9920')
print(len(words9920))
print(words9920)

# e
prep_in_9920 = 0
preps = ['about', 'beside', 'above', 'near', 'to', 'of', 'than']
for word in words9920:
    if word.lower() in preps:
        prep_in_9920 += 1

print(prep_in_9920)

# 5
table_dict = {}
for category in reuters.categories():
    table_dict[category] = reuters.fileids(category)
    # print(f'Category: {category} and fileIDS: {reuters.fileids(category)}')
print(table_dict)


# 6
def word_freq(word, file_id):
    freq = FreqDist(file_id)
    return freq[word]


# Change fileid to actual corpus object
test_fileid = reuters.words("test/15271")
word = "wheat"

print(f'Frequency distribution: {word_freq(word, test_fileid)}')
