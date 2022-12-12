from django.contrib import admin

from .models import Article, ArticleGroup, DatasetArticle, Recommendation


admin.site.register(Article)
admin.site.register(ArticleGroup)
admin.site.register(DatasetArticle)
admin.site.register(Recommendation)
