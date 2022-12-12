import pandas as pd
from nltk import FreqDist
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class TextAnalyzer:

    def extract_keyword(self, text, word_count=5):

        freq = FreqDist(text.split(' '))
        freq_list = pd.DataFrame(freq.most_common(word_count),
                                 columns=['Word', 'Frequency'])
        self.keywords = freq_list["Word"].to_numpy().tolist()

        return self.keywords

    def get_similarity(self, doc1, doc2):

        vectorizer = TfidfVectorizer()

        v1 = vectorizer.fit_transform(doc1)
        v2 = vectorizer.transform(doc2)

        similarity = cosine_similarity(v1, v2)

        return round(similarity.mean(axis=0)[0], 3)*100
