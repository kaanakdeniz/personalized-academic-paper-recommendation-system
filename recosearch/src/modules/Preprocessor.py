import re
from nltk.tokenize import word_tokenize


class Preprocessor:

    def __init__(self):

        with open('utils/stopwords.txt', "r") as f:
            self.stopwords = f.read().split('\n')

    def clear_text(self, text):

        text = text.lower()
        text = re.sub("</?.*?>", " <> ", text)
        text = re.sub("(\\d|\\W)+", " ", text)
        self.text = text

        return self.text

    def clear_stopwords(self, text):

        self.tokens = word_tokenize(text)

        self.text = [
            word for word in self.tokens if not word in self.stopwords and len(word) > 2]

        return ' '.join(self.text)
