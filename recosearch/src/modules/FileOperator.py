import os


class FileOperator:

    def get_user_articles_path(self, path):

        article_list = os.listdir(path)
        return article_list
