from django.contrib.auth.models import User
from djongo import models

from .validators import validate_file_extension


def user_directory_path(instance, filename):
    return '{0}/{1}/{2}'.format(instance.article_group.profile, instance.article_group, filename)


class Author(models.Model):
    author = models.CharField(max_length=100)

    class Meta:
        abstract = True

    def __str__(self):
        return self.author


class Keyword(models.Model):
    word = models.CharField(max_length=20)

    class Meta:
        abstract = True

    def __str__(self):
        return self.word


class ArticleGroup(models.Model):
    profile = models.ForeignKey(User, on_delete=models.CASCADE)
    groupname = models.CharField(max_length=255)

    def __str__(self):
        return self.groupname

    class Meta:
        verbose_name = "Article Group"


class Article(models.Model):
    article_group = models.ForeignKey(ArticleGroup, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    text = models.TextField(null=True, blank=True)
    keywords = models.ArrayField(model_container=Keyword)
    file = models.FileField(upload_to=user_directory_path, validators=[validate_file_extension])

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Article"


class DatasetArticle(models.Model):
    authors = models.ArrayField(model_container=Author,null=True)
    article_group = models.ForeignKey(ArticleGroup, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    text = models.TextField(null=True, blank=True)
    keywords = models.ArrayField(model_container=Keyword)
    summary = models.TextField()
    published_date = models.DateTimeField(null=True)
    pdf_link = models.CharField(max_length=255)
    relation_score = models.FloatField(null=True, blank=True)
    similarity_score = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Dataset Article"


class Recommendation(models.Model):
    article_group = models.ForeignKey(
        ArticleGroup, on_delete=models.CASCADE, related_name="Article")
    recommended_article = models.ForeignKey(DatasetArticle, on_delete=models.CASCADE)
    similarity_score = models.FloatField(null=True)
    relation_score = models.FloatField(null=True)

    def __str__(self):
        return self.article_group.groupname

    class Meta:
        verbose_name = "Recommendation"
