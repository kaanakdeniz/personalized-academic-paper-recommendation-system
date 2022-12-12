import pandas as pd

from modules.APIOperator import APIOperator
from modules.TextAnalyzer import TextAnalyzer


class TextAnalyzerTest:

    def __init__(self):
        self.doc1 = pd.read_csv("profile.csv")['text'][0]
        self.doc2 = pd.read_csv("query2.csv")['summary'][0]
        self.analyzer = TextAnalyzer()

    def test_extract_keywords(self,word_count=5):
        keywords = self.analyzer.extract_keyword(self.doc1, word_count=word_count)

        if len(keywords) == word_count:
            return True

        return False

    def test_get_similarity(self):
        similarity = self.analyzer.get_similarity([self.doc1], [self.doc2])/100

        if 0 <= similarity <= 1:
            return True

        return False


class APIOperatorTest:

    def __init__(self):
        self.apiopt = APIOperator()
        self.keywords = eval(pd.read_csv("profile.csv")['keywords'][0])

    def test_get_query_urls(self):
        self.urls = self.apiopt.create_query_urls(self.keywords)

        if self.urls:
            return True

        return False

    def test_get_article_querys(self):
        self.results = self.apiopt.get_article_queries(self.urls)

        if not self.results.empty:
            return True

        return False

if __name__ == "__main__":    

    tester1 = TextAnalyzerTest()
    tester2 = APIOperatorTest()

    result1 = tester1.test_get_similarity()
    result2 = tester1.test_extract_keywords()
    result3 = tester2.test_get_query_urls()
    result4 = tester2.test_get_article_querys()

    print("Text analyze test result: ",result1)
    print("Keyword extraction test result: ",result2)
    print("Create query urls test result: ",result3)
    print("Get query results test result: ",result4)
