from os import listdir
from os.path import isfile, join
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer as tf_idf


class Cluster:
    def __init__(self, path):
        self.path = path
        self.file_list = sorted([path + f for f in listdir(path) if isfile(join(path, f))])
        self.docs = {}
        self.vectorizer = tf_idf(
            input='filename',
            max_df=0.95,
            stop_words="english",
        )

    def vectorize(self):
        return self.vectorizer.fit_transform(self.file_list[:6])  # Change to how many docs you want to vectorize

    def cluster_files(self, matrix, k):
        number_of_clusters = k
        km = KMeans(n_clusters=number_of_clusters)
        km.fit(matrix)
        filename = f"Cluster_k-{k}.txt"
        out = open(filename, "w")
        out.write("K means with k = " + str(k) + "\n")
        order_centroids = km.cluster_centers_.argsort()[:, ::-1]
        terms = self.vectorizer.get_feature_names_out()
        for i in range(number_of_clusters):
            top_twenty_words = [terms[ind] for ind in order_centroids[i, :20]]
            out.write(f"Cluster {i}: {top_twenty_words}\n")
        results = pd.DataFrame({
            'text': self.file_list[:6],
            'category': km.labels_
        })
        out.write(results.to_string())
        out.close()
