from Cluster import Cluster
import pandas as pd
from Scraper import Scraper

# Scrape files
s = Scraper("concordia/test_html")
s.scrape_files()

# Vectorize documents into tf-idf matrix
cluster = Cluster("docs/")
matrix = cluster.vectorize()
print(matrix.shape)  # (Number of docs, number of words in vocabulary)
# 2D array array[doc, word]
df = pd.DataFrame(matrix.toarray(), columns=cluster.vectorizer.get_feature_names_out())
# Finding top 20 words, afinn score of each cluster and writing to file
cluster.cluster_files(matrix, 3)  # Cluster_k-3.txt
cluster.cluster_files(matrix, 6)  # Cluster_k-6.txt
