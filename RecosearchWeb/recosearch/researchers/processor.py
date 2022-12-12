import os
import re
from io import StringIO
from itertools import chain, combinations
from urllib.request import urlretrieve as get

import pandas as pd
import requests
import untangle
from django.conf import settings
from nltk import FreqDist
from nltk.tokenize import word_tokenize
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class APIOperator:

    def create_query_urls(self, iterable, max_results=5):

        urls = []
        for query in iterable:
            urls.append("http://export.arxiv.org/api/query?search_query=all:" +
                        query + "&max_results="+str(max_results))

        return urls

    def parse_xml(self, url):

        page = requests.get(url).text
        xml = untangle.parse(page)
        feed = xml.feed

        return feed

    def get_articles(self, feed):

        articles = []

        try:
            for item in feed.entry:
                title = item.title.cdata
                summary = item.summary.cdata
                pdf = item.id.cdata
                pdf = pdf.replace("abs", "pdf")
                published_date = item.published.cdata
                authors = [author.name.cdata for author in item.author]
                article = {
                    "title": title,
                    "summary": summary,
                    "pdf": pdf,
                    "published_date": published_date,
                    "authors": authors
                }
                articles.append(article)
        except:
            pass

        return articles

    def get_one_query(self, url):

        df = pd.DataFrame()

        xml = self.parse_xml(url)

        articles = self.get_articles(xml)
        df_temp = pd.DataFrame(articles)
        df = pd.concat([df, df_temp])

        return df

    def get_article_queries(self, urls):

        df = pd.DataFrame()

        for url in urls:
            xml = self.parse_xml(url)

            articles = self.get_articles(xml)
            df_temp = pd.DataFrame(articles)
            df = pd.concat([df, df_temp])

        df = df.drop_duplicates(subset=["title"], keep="first")

        return df


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


class PDFReader:

    def __init__(self):

        self.codec = 'utf-8'
        self.laparams = LAParams()

    def read_text(self, path):

        rsrcmgr = PDFResourceManager()
        retstr = StringIO()
        device = TextConverter(
            rsrcmgr, retstr, codec=self.codec, laparams=self.laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        with open(path, 'rb') as file:
            for page in PDFPage.get_pages(file):
                interpreter.process_page(page)

        text = retstr.getvalue()

        device.close()
        retstr.close()

        return text

    def download_and_read(self, title, url):

        filepath = "dataset/"+title+".pdf"
        get(url, filepath)
        text = self.read_text(filepath)
        return text


class Preprocessor:

    def __init__(self):
        path = os.path.join(settings.UTILS, 'stopwords.txt')
        with open(path, "r") as f:
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


class Processor:

    def __init__(self):
        self.pdf = PDFReader()
        self.preprocessor = Preprocessor()
        self.analyzer = TextAnalyzer()
        self.api = APIOperator()

    def create_article_information(self, path, word_count=2):

        text = self.pdf.read_text(path)
        text = self.preprocessor.clear_text(text)
        text = self.preprocessor.clear_stopwords(text)
        keywords = self.analyzer.extract_keyword(
            text, word_count=word_count)

        article = {
            "text": text,
            "keywords": keywords
        }

        return article

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
