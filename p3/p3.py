#!/usr/bin/env python
# coding: utf-8

# In[82]:


from nltk.tokenize import RegexpTokenizer
from nltk import word_tokenize
import time
from math import log


# ## Getting subcorpus of 10,000 tokens

# In[83]:


content_tokenizer = RegexpTokenizer('<TEXT.*?>(.*?)</TEXT>')
article_tokenizer = RegexpTokenizer('<REUTERS(.*?)</REUTERS>')
id_tokenizer = RegexpTokenizer('NEWID="(.*?)"')
metadata_tokenizer = RegexpTokenizer('<.*?>')
html_entities_tokenizer = RegexpTokenizer('^&.*?;')
token_count = 0
sub_corpus = []


def remove_metadata(text):
    tags = metadata_tokenizer.tokenize(text)
    html_entities = html_entities_tokenizer.tokenize(text)
    metadata = tags + html_entities
    if len(metadata) > 0:
        for element in metadata:
            text = text.replace(element, '')
    return text


def remove_punctuation(tokens):
    punctuation_list = [*".,:;-<>{}()[]~`&*?"]
    double_symbols = ['""', "''", "``", "...", "--", "-", ","]
    punctuation_list += double_symbols
    for t in tokens:
        if t in punctuation_list:
            tokens.remove(t)
    return tokens


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

        for article in articles:
            ID = id_tokenizer.tokenize(article)[0]  # Get ID
            contents = content_tokenizer.tokenize(article)  # Get content inside <TEXT> tags
            contents = ' '.join(contents)
            contents = remove_metadata(contents)
            # Tokenize article content, need to get title and body
            tokens = word_tokenize(contents)
            tokens = remove_punctuation(tokens)
            # Add ID to sub_corpus element
            sub_corpus.append([ID])
            article_tokens = []
            for token in tokens:
                token_count += 1
                if token_count < 10000:
                    article_tokens.append(token)
                else:
                    sub_corpus[int(ID) - 1].append(article_tokens)
                    raise StopIteration
            sub_corpus[int(ID) - 1].append(article_tokens)
    except IOError:
        print("Error: File does not exist")
    except StopIteration:
        print("Reached 10,000 tokens")
        break


# In[84]:


print(sub_corpus)


# ## Naive indexer code

# In[85]:


f = []

# Start timer
start_time = time.time()

# Get doc,ID pairs

for i in range(len(sub_corpus)):
    for token in sub_corpus[i][1]:
        f.append((sub_corpus[i][0], token))

# Sort and remove duplicates
f.sort(key=lambda x: int(x[0]))
f = list(dict.fromkeys(f))
index_naive = {}
for pair in f:
    # Pair[0] is docID and pair[1] is word
    if pair[1] in index_naive:
        index_naive[pair[1]].append(pair[0])
    else:
        index_naive[pair[1]] = [pair[0]]
# End timer
print(f"Naive indexer took: {(time.time() - start_time)} seconds")


# ## SPIMI indexer

# In[87]:


index_spimi = {}

# Start timer
start_time = time.time()
token_count = 0

for article in sub_corpus:
    ID = article[0]
    for token in article[1]:
        if token in index_spimi:
            if not ID in index_spimi[token]:
                index_spimi[token].append(ID)
        else:
            index_spimi[token] = [ID]
# End timer
print(f"SPIMI indexer took: {(time.time() - start_time)} seconds")


# ## Create inverted index without compression techniques

# ### Create corpus of reuters in the form (ID,tokens)

# In[91]:


reuters_corpus = []
index_corpus = {}

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
        for article in articles:
            ID = id_tokenizer.tokenize(article)[0]  # Get ID
            contents = content_tokenizer.tokenize(article)  # Get content inside <TEXT> tags
            contents = ' '.join(contents)
            contents = remove_metadata(contents)
            tokens = word_tokenize(contents)
            reuters_corpus.append((ID, tokens))
    except IOError:
        print("Error: File does not exist")


# ### Indexing

# In[92]:


# Start timer
start_time = time.time()
for article in reuters_corpus:
    ID = article[0]
    tokens = set(article[1])
    for token in tokens:
        if token in index_corpus:
            index_corpus[token].append(ID)
        else:
            index_corpus[token] = [ID]
# End timer
print(f"Whole corpus indexer took: {(time.time() - start_time)} seconds")


# # Subproject 2
# 

# ## Create index with term frequency

# In[94]:


inverted_index = {}
doc_len_list = []
for doc in reuters_corpus:
    ID = doc[0]
    doc_len_list.append(len(doc[1]))  # Appends doc length for use in BM25
    tokens = remove_punctuation(doc[1])
    no_duplicates = set(tokens)
    for token in no_duplicates:
        freq = tokens.count(token)
        if token in inverted_index:
            if not ID in inverted_index[token]:
                inverted_index[token][ID] = freq
        else:
            inverted_index[token] = {ID: freq}


# In[95]:


avg_doc_len = int(sum(doc_len_list) / len(doc_len_list))
total_doc_num = len(reuters_corpus)


def compute_bm25(tf, df, doc_len, k, b):
    log_part = log(total_doc_num / df)
    numerator = (k + 1) * tf
    denominator = (k * ((1 - b) + b * (doc_len / avg_doc_len))) + tf
    score = log_part * (numerator / denominator)
    return score


# Modes are bm25, AND, OR
def process_query(query, mode):
    query = set(word_tokenize(query))
    results = []
    # OR query
    if mode == "OR":
        results = {}
        for element in query:
            if element in inverted_index:
                for ID, tf in inverted_index[element].items():
                    if ID in results:
                        results[ID] += tf
                    else:
                        results[ID] = tf
        results = sorted(results.items(), key=lambda item: item[1], reverse=True)
        results = [x[0] for x in results]
    elif mode == "AND":
        for element in query:
            if element in inverted_index:
                results.append(list(inverted_index[element].keys()))
        # Find intersection
        intersection = set(results[0])
        for x in results[1:]:
            temp_list = set(x) & intersection
            intersection = temp_list
        results = intersection
    elif mode == "BM25":
        k = 1.1
        b = 0.5
        results = {}
        for word in query:
            if word in inverted_index:
                df = len(inverted_index[word])
                for doc in inverted_index[word].keys():
                    tf = inverted_index[word][doc]
                    doc_len = len(reuters_corpus[int(doc) - 1][1])  # len of doc
                    # print(doc)
                    # print(tf)
                    # print(df)
                    # print(doc_len)
                    score = compute_bm25(tf, df, doc_len, k, b)
                    if word in results:
                        results[doc] += score
                    else:
                        results[doc] = score
        results = sorted(results.items(), key=lambda item: item[1], reverse=True)
        results = [x[0] for x in results]
    return results


# ## Test queries

# In[96]:


test_query_a = "Samjens"
print(process_query(test_query_a, "BM25"))  # Returns list of IDs, for OR and BM25 they are ordered by docID


# In[97]:


test_query_b = "Smith likes play football"
print(process_query(test_query_b, "BM25"))  # Returns list of IDs, for OR and BM25 they are ordered by docID


# In[53]:


test_query_c = "Hong Kong investment firm"
print(process_query(test_query_c, "AND"))  # Returns list of IDs, for OR and BM25 they are ordered by docID


# In[63]:


test_query_d = "Concordia university"
print(process_query(test_query_d, "OR"))  # Returns list of IDs, for OR and BM25 they are ordered by docID


# In[98]:


deliverables_queries = ['Democrats’ welfare and healthcare reform policies', 'Drug company bankruptcies', 'George Bush']
f = open("test_queries.txt", "w")
for x in deliverables_queries:
    f.write("Query: ")
    f.write(str(x))
    f.write(str(process_query(x, "BM25")))
    print("Digestible format")
    print("Query: " + x)
    print(process_query(x, "BM25")[:20])
f.close()


# In[ ]:




