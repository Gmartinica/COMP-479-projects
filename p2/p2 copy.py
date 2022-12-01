#!/usr/bin/env python
# coding: utf-8

# In[300]:


from nltk.tokenize import RegexpTokenizer
from nltk import word_tokenize
from nltk.stem.porter import PorterStemmer
from tabulate import tabulate


# ### Input document name and add content to postings list

# In[301]:


content_tokenizer = RegexpTokenizer('<TEXT.*?>(.*?)</TEXT>')
article_tokenizer = RegexpTokenizer('<REUTERS(.*?)</REUTERS>')
id_tokenizer = RegexpTokenizer('NEWID="(.*?)"')
metadata_tokenizer = RegexpTokenizer('<.*?>')
html_entities_tokenizer = RegexpTokenizer('^&.*?;')
postings_list = {}
f = []
reuters_corpus = []


def remove_metadata(text):
    tags = metadata_tokenizer.tokenize(text)
    html_entities = html_entities_tokenizer.tokenize(text)
    metadata = tags + html_entities
    if len(metadata) > 0:
        for element in metadata:
            text = text.replace(element, '')
    return text


while True:
    document = input("Please enter document: ")
    if document == "exit()":  # Exit the loop
        break
    elif document == "reuters_corpus":  # Get all sgm files from the reuters corpus and use that as index (Automatic index creation) (For testing queries)
        for i in range(22):
            doc = f"./reuters21578/reut2-0{i:02d}.sgm"
            try:
                if i != 17:
                    with open(doc, 'rt') as file:
                        file = file.read()
                else:
                    # Needed as file 17 gave me UnicodeDecodeError
                    file = open(doc, mode="rb")
                    file = file.read()
                    file = str(file)
                articles = article_tokenizer.tokenize(file)
                reuters_corpus += articles

                for article in articles:
                    ID = id_tokenizer.tokenize(article)[0]
                    contents = content_tokenizer.tokenize(article)
                    contents = ' '.join(contents)
                    contents = remove_metadata(contents)
                    tokens = word_tokenize(contents)
                    for token in tokens:
                        f.append((ID, token))
            except IOError:
                print("Error: File does not exist")

    else:  # Let user select the file to be added to index
        document = './reuters21578/' + document
        contents = ''
        try:
            with open(document, 'rt') as file:
                contents = file.read()
        except IOError:
            print("Error: File does not exist")
        finally:
            file.close()

        articles = article_tokenizer.tokenize(contents)
        for article in articles:
            ID = id_tokenizer.tokenize(article)[0]
            contents = content_tokenizer.tokenize(article)
            contents = ' '.join(contents)
            contents = remove_metadata(contents)
            # Tokenize article content, need to get title and body
            tokens = word_tokenize(contents)
            for token in tokens:
                f.append((ID, token))


# ## Sort F and remove duplicates

# In[302]:


f.sort(key=lambda x: int(x[0]))
print(f[:300])


# In[303]:


f = list(dict.fromkeys(f))


# 

# In[304]:


postings_list = {}
for pair in f:
    # Pair[0] is docID and pair[1] is word
    if pair[1] in postings_list:
        postings_list[pair[1]].append(pair[0])
    else:
        postings_list[pair[1]] = [pair[0]]


# ## Query processor

# In[305]:


def query_processor(postings, query):
    res = ''
    if query in postings:
        print(f"Query for word {query} retrieved successfully. The results are:\n{postings[query]}")
        res = postings[query]
    elif query == "exit()":
        print("Thank you for using the query processor. See you next time!")
    else:
        print("Query not found in postings list")
    return res


query = None
while query != "exit()":
    query = input("Please enter the word to search: (Type exit() to stop)")
    result = query_processor(postings_list, query)


# ## Validate 3 queries

# In[306]:


query1 = "exit"
query2 = "business"
query3 = "stocks"

test_queries = {query1: query_processor(postings_list, query1),
                query2: query_processor(postings_list, query2),
                query3: query_processor(postings_list, query3)}

# Validate queries
for query in test_queries:
    ids = test_queries[query]
    for number in ids:
        newID = int(number) - 1
        if query in reuters_corpus[newID]:
            print(f"✓ {query} was FOUND in the article with id: {newID + 1}")
        else:
            print(f"✕{query} was NOT FOUND in the article with id: {newID + 1}")


# In[307]:


challenge_queries = ['copper', 'Samjens', 'Carmark', 'Bundesbank']
res_txt = open("challenge_queries_results.txt", "w")
for word in challenge_queries:
    result = query_processor(postings_list, word)
    res_txt.write(f"\nResults for query {word} are the following:\n{result}")

res_txt.close()


# ## Implement lossy dictionary compression

# In[308]:


def find_stop_words(postings):
    sorted_postings = sorted([(len(v), k) for k, v in postings.items()], reverse=True)
    sorted_postings = sorted_postings[:150]
    common_stop_words = [x[1] for x in sorted_postings]
    return common_stop_words


# In[309]:


# Distinct terms
unfiltered_terms = [key for key in postings_list]
no_numbers_terms = [word for word in unfiltered_terms if not word.isnumeric()]
case_folding_terms = {w.lower() for w in no_numbers_terms}  # set
stop_words_150 = find_stop_words(postings_list)
stop_words_30 = stop_words_150[:30]
remove_30_stop_words = {w for w in case_folding_terms if w not in stop_words_30}
remove_150_stop_words = {w for w in case_folding_terms if w not in stop_words_150}
porter = PorterStemmer()
porter_stemmed = {porter.stem(word) for word in remove_150_stop_words}


# In[310]:


def percentage_diff(num1, num2):
    average = (num1 + num2) / 2
    diff = abs(num1 - num2)
    return int(diff / average * 100)


table_terms = {'Sections': ['unfiltered', 'no numbers', 'case folding', '30 stop words', '150 stop words', 'stemming'],
               'numbers': [len(unfiltered_terms), len(no_numbers_terms), len(case_folding_terms),
                           len(remove_30_stop_words),
                           len(remove_150_stop_words), len(porter_stemmed)],
               '∆%': ['', percentage_diff(len(unfiltered_terms), len(no_numbers_terms)),
                      percentage_diff(len(no_numbers_terms), len(case_folding_terms)),
                      percentage_diff(len(case_folding_terms), len(remove_30_stop_words)),
                      percentage_diff(len(case_folding_terms), len(remove_150_stop_words)),
                      percentage_diff(len(remove_150_stop_words), len(porter_stemmed))],
               'T%': ['', percentage_diff(len(unfiltered_terms), len(no_numbers_terms)),
                      percentage_diff(len(unfiltered_terms), len(case_folding_terms)),
                      percentage_diff(len(unfiltered_terms), len(remove_30_stop_words)),
                      percentage_diff(len(unfiltered_terms), len(remove_150_stop_words)),
                      percentage_diff(len(unfiltered_terms), len(porter_stemmed))]}
print(tabulate(table_terms, headers="keys", tablefmt='fancy_grid', missingval='N/A'))


# In[311]:


def len_posts(postings):
    length = 0
    for key in postings:
        length += len(postings[key])
    length += len(postings)
    return length


unfiltered_postings = len_posts(postings_list)

# Remove numbers
for word in unfiltered_terms:
    if word.isnumeric():
        del postings_list[word]

no_numbers_postings = len_posts(postings_list)


# In[312]:


# Casefold
for word in no_numbers_terms:
    if word.lower() in postings_list:
        if postings_list[word.lower()] != postings_list[word]:
            # Find union of lists
            union = list(set().union(postings_list[word.lower()], postings_list[word]))
            postings_list[word.lower()] = union
            del postings_list[word]
    else:
        postings_list[word.lower()] = postings_list[word]
        del postings_list[word]

case_folding_postings = len_posts(postings_list)


# In[313]:


# Remove 30 stop words
for word in stop_words_30:
    if word in postings_list:
        del postings_list[word]

remove_30_stop_words_postings = len_posts(postings_list)
# Remove 150 stop words
for word in stop_words_150:
    if word in postings_list:
        del postings_list[word]

remove_150_stop_words_postings = len_posts(postings_list)


# In[314]:


# Stemming
for word in remove_150_stop_words:
    if porter.stem(word) in postings_list:
        if postings_list[porter.stem(word)] != postings_list[word]:
            # Find union of lists
            union = list(set().union(postings_list[porter.stem(word)], postings_list[word]))
            postings_list[porter.stem(word)] = union
            del postings_list[word]
    else:
        postings_list[porter.stem(word)] = postings_list[word]
        del postings_list[word]
stem_postings = len_posts(postings_list)


# In[315]:


table_terms = {'Sections': ['unfiltered', 'no numbers', 'case folding', '30 stop words', '150 stop words', 'stemming'],
               'numbers': [unfiltered_postings, no_numbers_postings, case_folding_postings,
                           remove_30_stop_words_postings,
                           remove_150_stop_words_postings, stem_postings],
               '∆%': ['', percentage_diff(unfiltered_postings, no_numbers_postings),
                      percentage_diff(no_numbers_postings, case_folding_postings),
                      percentage_diff(case_folding_postings, remove_30_stop_words_postings),
                      percentage_diff(remove_30_stop_words_postings, remove_150_stop_words_postings),
                      percentage_diff(remove_150_stop_words_postings, stem_postings)],
               'T%': ['', percentage_diff(unfiltered_postings, no_numbers_postings),
                      percentage_diff(unfiltered_postings, case_folding_postings),
                      percentage_diff(unfiltered_postings, remove_30_stop_words_postings),
                      percentage_diff(unfiltered_postings, remove_150_stop_words_postings),
                      percentage_diff(unfiltered_postings, stem_postings)]}
print(tabulate(table_terms, headers="keys", tablefmt='fancy_grid', missingval='N/A'))


# In[316]:


res_txt = open("challenge_queries_results_2.txt", "w")
for word in challenge_queries:
    result = query_processor(postings_list, word)
    res_txt.write(f"\nResults for query {word} are the following:\n{result}")

res_txt.close()


# In[317]:


for query in test_queries:
    ids = test_queries[query]
    for number in ids:
        newID = int(number) - 1
        if query in reuters_corpus[newID]:
            print(f"✓ {query} was FOUND in the article with id: {newID + 1}")
        else:
            print(f"✕{query} was NOT FOUND in the article with id: {newID + 1}")


# In[317]:




