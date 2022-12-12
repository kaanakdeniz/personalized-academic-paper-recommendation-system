import django_tables2 as tables
from .models import Article, ArticleGroup, DatasetArticle, Recommendation
from django.utils.html import format_html
import itertools


class ArticleTable(tables.Table):
    n = tables.Column(empty_values=(), verbose_name='')
    detail = '<a class="btn btn-success btn-sm" href="{% url "article-detail" record.id%}"><i class="fas fa-info-circle mr-2"></i>Detail</a>'
    delete = '<a class="btn btn-danger btn-sm" href="{% url "article-delete" record.id%}"><i class="fas fa-eraser mr-2"></i>Delete</a>'
    article_group = '<a href="{% url "group-detail" record.article_group.id%}">{{ record.article_group }}</a>'
    detail = tables.TemplateColumn(detail, orderable=False)
    delete = tables.TemplateColumn(delete, orderable=False)
    title = tables.Column(
        attrs={'td': {'class': 'text-left'}, 'th': {'class': 'w-50 text-left'}})
    article_group = tables.TemplateColumn(
        article_group, verbose_name="Article Group", orderable=False)
    file = tables.Column(orderable=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.counter = itertools.count(start=1)

    def render_n(self):
        return "%d" % next(self.counter)

    def render_file(self, value, record):
        return format_html('<a class="btn btn-warning btn-sm" target="_blank" href="/documents/{}"><i class="far fa-file-pdf mr-2"></i>File</a>', record.file)

    class Meta:
        model = Article
        empty_text = "No results found!"
        fields = ('n', 'article_group', 'title', 'file')
        attrs = {'thead': {'class': 'thead-light'},
                 'class': 'table table-bordered text-center'
                 }


class ArticleGroupTable(tables.Table):

    n = tables.Column(empty_values=(), verbose_name='')
    detail = '<a class="btn btn-success btn-sm" href="{% url "group-detail" record.id%}"><i class="fas fa-info-circle mr-2"></i>Detail</a>'
    delete = '<a class="btn btn-danger btn-sm" href="{% url "group-delete" record.id%}"><i class="fas fa-eraser mr-2"></i>Delete</a>'
    recommend = '<a class=" btn btn-info btn-sm text-white" onclick="loadBar()" href="{% url "group-recommend" record.id%}"><span class="reco-icon mr-1">Ø</span>Recommend</a> '
    recommend = tables.TemplateColumn(recommend, orderable=False)
    detail = tables.TemplateColumn(detail, orderable=False)
    delete = tables.TemplateColumn(delete, orderable=False)
    n_articles = tables.Column(
        empty_values=(), verbose_name='# of Articles', orderable=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.counter = itertools.count(start=1)

    def render_n(self):
        return "%d" % next(self.counter)

    def render_n_articles(self, value, record):
        return Article.objects.filter(article_group=record).count()

    class Meta:
        model = ArticleGroup
        empty_text = "No results found!"
        fields = ('n', 'groupname', 'n_articles')
        attrs = {'thead': {'class': 'thead-light'},
                 'class': 'table table-bordered text-center'
                 }


class DatasetArticleTable(tables.Table):
    n = tables.Column(empty_values=(), verbose_name='')
    detail = '<a class="btn btn-success btn-sm" href="{% url "related-detail" record.id %}"><i class="fas fa-info-circle mr-2"></i>Detail</a>'
    delete = '<a class="btn btn-danger btn-sm" href="{% url "related-delete" record.id %}"><i class="fas fa-eraser mr-2"></i>Delete</a>'
    detail = tables.TemplateColumn(detail, orderable=False)
    delete = tables.TemplateColumn(delete, orderable=False)
    title = tables.Column(
        attrs={'td': {'class': 'text-left'}, 'th': {'class': 'w-50 text-left'}})
    pdf_link = tables.Column(orderable=False, verbose_name="PDF")
    relation_score = tables.Column(verbose_name='Relation Score')
    article_group = '<a href="{% url "group-detail" record.article_group.id%}">{{ record.article_group }}</a>'
    article_group = tables.TemplateColumn(
        article_group, verbose_name="Article Group",orderable=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.counter = itertools.count(start=1)

    def render_n(self):
        return "%d" % next(self.counter)

    def render_relation_score(self, value):
        return "%" + str(value)[0:4]

    def render_pdf_link(self, value, record):
        return format_html('<a class="btn btn-warning btn-sm" target="_blank" href="{}"><i class="far fa-file-pdf mr-2"></i>PDF</a>', record.pdf_link)

    class Meta:
        model = DatasetArticle
        empty_text = "No results found!"
        fields = ('n', 'article_group', 'title', 'relation_score', 'pdf_link')
        attrs = {'thead': {'class': 'thead-light'},
                 'class': 'table table-bordered text-center'
                 }


class RecommendationsTable(tables.Table):
    n = tables.Column(empty_values=(), verbose_name='')
    relation_score = tables.Column(verbose_name="Relation Score")
    similarity_score = tables.Column(
        verbose_name="Similarity Score", empty_values=[])
    recommended_article = tables.Column(
        attrs={'td': {'class': 'text-left'}, 'th': {'class': 'w-50 text-left'}}, orderable=False)
    detail = '<a class="btn btn-success btn-sm" href="{% url "related-detail" record.recommended_article.id %}"><i class="fas fa-info-circle mr-2"></i>Detail</a>'
    detail = tables.TemplateColumn(detail, orderable=False)
    article_group = '<a href="{% url "group-detail" record.article_group.id%}">{{ record.article_group }}</a>'
    article_group = tables.TemplateColumn(
        article_group, verbose_name="Article Group",orderable=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.counter = itertools.count(start=1)

    def render_similarity_score(self, value, record):
        if value:
            return "%" + str(value)[0:4]
        else:
            return format_html('<a onclick="loadBar2()" id="analyze" class="btn btn-primary btn-sm"' +
                               ' href="/dataset-article/{}/analyze"><i class="fas fa-book-reader mr-2"></i>Analyze</a>', record.recommended_article.id)

    def render_relation_score(self, value):
        return "%" + str(value)[0:4]

    def render_n(self):
        return "%d" % next(self.counter)

    class Meta:
        model = Recommendation
        empty_text = "No results found!"
        fields = ('n', 'article_group',
                  'recommended_article', 'relation_score', 'similarity_score')
        attrs = {'thead': {'class': 'thead-light'},
                 'class': 'table table-bordered text-center'
                 }
