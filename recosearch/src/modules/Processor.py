import os

import pandas as pd

from modules.APIOperator import APIOperator
from modules.FileOperator import FileOperator
from modules.PDFReader import PDFReader
from modules.Preprocessor import Preprocessor
from modules.TextAnalyzer import TextAnalyzer


class Processor:

    def __init__(self):
        self.pdf = PDFReader()
        self.preprocessor = Preprocessor()
        self.analyzer = TextAnalyzer()
        self.api = APIOperator()
        self.fops = FileOperator()

    def create_article_information(self, article_name, dir="data", word_count=2):

        path = os.path.join(dir, article_name+".pdf")

        text = self.pdf.read_text(path)
        text = self.preprocessor.clear_text(text)
        text = self.preprocessor.clear_stopwords(text)
        keywords = self.analyzer.extract_keyword(
            text, word_count=word_count)

        article = {
            "title": article_name,
            "text": text,
            "keywords": keywords
        }

        return article

    def create_group_information(self, dir="data", word_count=2):

        articles = []

        paths = self.fops.get_user_articles_path(dir)

        for file in paths:

            path = os.path.join(dir, file)
            filename = file.replace(".pdf", "")

            article = self.create_article_information(
                filename, word_count=word_count)

            articles.append(article)

        return pd.DataFrame(articles)

    def create_group_dataset(self, profile):

        df = pd.DataFrame()

        for keywords in zip(profile.keywords):
            queries = self.api.create_query_urls(keywords[0])
            df = pd.concat([df, self.api.get_article_queries(queries)])

        return df

    def get_article_similarities(self, article, dArticle):

        score = self.analyzer.get_similarity(article[1], dArticle[1])

        similarity = {
            "profile_article": article[0],
            "dataset_article": dArticle[0],
            "similarity": score
        }

        return similarity

    def get_profile_similarities(self, profile, dataset):

        similarities = []

        for article in zip(profile.title, profile.text):

            for dArticle in zip(dataset.title, dataset.summary):

                similarity = self.get_article_similarities(article, dArticle)

                similarities.append(similarity)

        return pd.DataFrame(similarities)
