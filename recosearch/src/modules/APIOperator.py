from itertools import chain, combinations

import pandas as pd
import requests
import untangle


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
                article = {
                    "title": title,
                    "summary": summary,
                    "pdf": pdf
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
