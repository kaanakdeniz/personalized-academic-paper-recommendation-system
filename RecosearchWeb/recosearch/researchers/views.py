import asyncio
import os
from urllib.request import urlretrieve as get

import django_tables2 as tables
import pandas as pd
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Exists
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django_tables2 import RequestConfig

from .decorators import unauthenticated_user
from .forms import CreateArticleGroupForm, CreateUserForm
from .models import (Article, ArticleGroup, Author, DatasetArticle, Keyword,
                     Recommendation)
from .processor import PDFReader, Processor, TextAnalyzer
from .tables import (ArticleGroupTable, ArticleTable, DatasetArticleTable,
                     RecommendationsTable)


def pie_chart(request):
    labels = []
    data = []

    queryset = ArticleGroup.objects.filter(profile=request.user.id)

    for group in queryset:
        labels.append(group.groupname)
        count = Recommendation.objects.filter(article_group=group).count()
        data.append(count)

    return labels, data


def line_chart(request):
    labels = []
    data = []

    queryset = ArticleGroup.objects.filter(profile=request.user.id)

    for group in queryset:
        labels.append(group.groupname)
        count = DatasetArticle.objects.filter(article_group=group).count()
        data.append(count)

    return labels, data


def create_article_info(article, path, word_count=10):

    proc = Processor()
    keywordList = []
    information = proc.create_article_information(path, word_count=word_count)
    article.text = information['text']
    keywords = information['keywords']

    for keyword in keywords:
        keywordObj = Keyword()
        keywordObj.word = keyword
        keywordList.append(keywordObj)

    article.keywords = keywordList

    article.save()


def create_related_articles(articles, group):

    data = []
    for article in articles:
        words = []
        for word in article['keywords']:
            words.append(word.word)
            if len(words) == 5:
                break
        dt = {
            "title": article['title'],
            "keywords": words
        }
        data.append(dt)

    prc = Processor()
    df = pd.DataFrame(data)
    df = prc.create_group_dataset(df)
    df = df.drop_duplicates('title')
    for item in zip(df['title'], df['summary'], df['pdf'], df['published_date'], df['authors']):
        article = DatasetArticle(
            title=item[0], summary=item[1], pdf_link=item[2],
             article_group=group, published_date = item[3])
        personList=[]
        for author in item[4]:
            person = Author(author=author)
            personList.append(person)
        article.authors = personList
        article.save()


def create_relation_scores(group):

    analyzer = TextAnalyzer()

    articles = list(Article.objects.filter(
                    article_group=group).values_list('text'))
    article_texts = [text[0] for text in articles]

    datasetArticles = DatasetArticle.objects.filter(article_group=group)

    for article in datasetArticles:
        score = analyzer.get_similarity(article_texts, [article.summary])
        if score < 5:
            article.delete()
            continue
        else:
            article.relation_score = score
            article.save()
        if score > 10:
            article.relation_score = score
            article.save()
            rec = Recommendation()
            rec.article_group = group
            rec.recommended_article = article
            rec.relation_score = score
            rec.save()


def create_similarity_score(article, group):
    analyzer = TextAnalyzer()
    articles = list(Article.objects.filter(
        article_group=group).values_list('text'))
    article_texts = [text[0] for text in articles]
    reco = Recommendation.objects.get(recommended_article=article)
    score = analyzer.get_similarity(article_texts, [article.text])
    reco.similarity_score = score
    article.similarity_score = score
    article.save()
    reco.save()


def calculate_averages(request):

    count_sim = 0
    scores = 0
    avg_sim = 0
    avg_rel = 0

    recommends = Recommendation.objects.filter(
        article_group__profile=request.user)
    count_rel = recommends.count()

    for item in recommends:
        avg_rel += item.relation_score
        if item.similarity_score:
            count_sim += 1
            avg_sim += item.similarity_score

    if avg_sim != 0:
        avg_sim = avg_sim/count_sim
    if avg_rel != 0:
        avg_rel = avg_rel/count_rel

    return avg_sim, avg_rel


def modelFilter(Model, request):

    q1 = request.GET.get('filtername')
    q2 = request.GET.get('title')  
    noneFilter = 'Select Article Group'
    queryset = Model.objects.filter(article_group__profile=request.user)

    if q2:
        if Model == Recommendation:
            kwargs ={'{}__{}'.format("recommended_article","title__icontains"):q2}
        
        if Model == Article or Model == DatasetArticle:
            kwargs = {'{}'.format("title__icontains"):q2}

    if q1:  
        noneFilter = q1
        queryset = Model.objects.filter(article_group__profile=request.user).filter(
            article_group__groupname=q1)

        if q2 and q2 != '':
            queryset = queryset.filter(**kwargs)            

    if not q1:
        if q2 and q2 != '':
            queryset = Model.objects.filter(article_group__profile=request.user).filter(**kwargs)

    return queryset, noneFilter


def homePage(request):
    return render(request, 'user/homepage.html')


@unauthenticated_user
def registerPage(request):

    form = CreateUserForm()

    if request.method == 'POST':

        form = CreateUserForm(request.POST)

        if form.is_valid():

            form.save()
            user = form.cleaned_data.get('first_name')
            messages.success(request, f'Account was created for {user}')
            return redirect('login')

    context = {'form': form}
    return render(request, 'user/register.html', context)


@unauthenticated_user
def loginPage(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')

        else:
            messages.warning(request, 'Username or password is incorrect!')

    context = {}
    return render(request, 'user/login.html', context)


@login_required(login_url='login')
def logoutUser(request):

    logout(request)

    return redirect('main')


@login_required(login_url='login')
def dashboardPage(request):

    articleCount = Article.objects.filter(
        article_group__profile=request.user).count()
    datasetArticleCount = DatasetArticle.objects.filter(
        article_group__profile=request.user).count()
    recommendationCount = Recommendation.objects.filter(
        article_group__profile=request.user).count()

    articleGroup = ArticleGroup.objects.filter(profile_id=request.user.id)
    articleGroupCount = articleGroup.count()
    avg_sim, avg_rel = calculate_averages(request)

    labels1, data1 = pie_chart(request)
    labels2, data2 = line_chart(request)

    context = {
        "articleCount": articleCount,
        "articleGroupCount": articleGroupCount,
        'datasetArticleCount': datasetArticleCount,
        "recommendationCount": recommendationCount,
        "avg_sim": "%" + str(avg_sim)[0:4],
        "avg_rel": "%" + str(avg_rel)[0:4],
        "labels1": labels1,
        "data1": data1,
        "labels2": labels2,
        "data2": data2,
    }

    return render(request, 'user/dashboard.html', context)


@login_required
def articleGroupsPage(request):

    form = CreateArticleGroupForm()

    table = ArticleGroupTable(ArticleGroup.objects.filter(
        profile_id=request.user.id))
    RequestConfig(request).configure(table).paginate(
        page=request.GET.get("page", 1), per_page=7)

    if request.method == 'POST':
        form = CreateArticleGroupForm(request.POST)

        if form.is_valid():
            group = form.save(commit=False)

            if ArticleGroup.objects.filter(profile_id=request.user.id,
                                           groupname=group.groupname).exists():
                messages.warning(request, 'This group exist!')

                return redirect('group-list')

            group.profile = request.user
            group.save()
            messages.success(request, 'Article group created successfully!')

            return redirect('group-list')

    context = {
        'form': form,
        'table': table,
    }

    return render(request, 'articlegroup/articlegroups.html', context)


@login_required
def articleGroupDetailPage(request, pk):
    
    user = request.user
    group = ArticleGroup.objects.get(pk=pk)

    table = ArticleTable(Article.objects.filter(
        article_group=pk), exclude=('article_group'))
    RequestConfig(request).configure(table).paginate(
        page=request.GET.get("page", 1), per_page=7)

    if request.method == 'POST':
        
        for f in request.FILES.getlist('files'):
            if f.content_type != "application/pdf":
                messages.warning(request, 'Please select PDF file.')
                return redirect(request.path_info)

            article = Article()
            article.article_group = group
            article.file = f
            article.title = f.name.replace('.pdf', '')            

            if Article.objects.filter(article_group=group, title=article.title).exists():
                messages.warning(
                    request, 'Article group includes one or more of the articles you load!')
                return redirect(request.path_info)
            
            article.save()
            path = os.path.join(settings.MEDIA_ROOT, str(article.file))
            create_article_info(article, path)

        messages.success(request, 'Articles added to group successfully!')
        return redirect(request.path_info)
                

    context = {
        'group': group,
        'table': table
    }
    return render(request, 'articlegroup/articlegroup_detail.html', context)


@login_required
def articleGroupDelete(request, pk):

    group = get_object_or_404(ArticleGroup, pk=pk)
    group.delete()
    messages.success(request, 'Article group deleted successfully!')

    return redirect('group-list')

@login_required
def articleDetailPage(request, pk):
    article = Article.objects.get(pk=pk)

    context = {
        "article": article
    }

    return render(request, 'article/article_detail.html', context)


@login_required
def articleDelete(request, pk):

    article = get_object_or_404(Article, pk=pk)
    group = ArticleGroup.objects.get(groupname=article.article_group)
    article.delete()
    messages.success(request, 'Article deleted from group successfully!')
    return redirect("group-detail", group.id)


@login_required
def datasetArticleDetailPage(request, pk):

    article = DatasetArticle.objects.get(pk=pk)

    context = {
        "article": article
    }
    return render(request, 'article/relatedarticle_detail.html', context)


@login_required
def datasetArticleDelete(request, pk):

    article = get_object_or_404(DatasetArticle, pk=pk)
    group = ArticleGroup.objects.get(groupname=article.article_group)
    article.delete()
    messages.success(request, 'Article deleted from group successfully!')
    return redirect("group-recommendations", group.id)


@login_required
def updateRelatedArticles(request, pk):

    group = ArticleGroup.objects.get(pk=pk)
    articles = Article.objects.filter(
        article_group=pk).values('title', 'keywords')

    if not articles:
        messages.warning(request, 'Please add articles to group!')
        return redirect('group-detail', pk)

    datasetArticles = DatasetArticle.objects.filter(
        article_group=pk).delete()
    create_related_articles(articles, group)
    create_relation_scores(group)

    messages.success(
        request, f'Related articles with {group} is updated successfully!')

    return redirect('group-recommendations', pk)


@login_required
def AllArticlesPage(request):

    articlegroups = ArticleGroup.objects.filter(profile=request.user) 
    queryset, noneFilter = modelFilter(Article, request)

    table = ArticleTable(queryset)
    RequestConfig(request).configure(table).paginate(
        page=request.GET.get("page", 1), per_page=7)

    context = {
        'table': table,
        'article_groups': articlegroups,
        'filter': noneFilter
    }

    return render(request, 'article/articles.html', context)


@login_required
def AllRelatedArticlesPage(request):

    articlegroups = ArticleGroup.objects.all()
    queryset, noneFilter = modelFilter(DatasetArticle, request)

    table = DatasetArticleTable(queryset, order_by=('-relation_score',))
    RequestConfig(request).configure(table).paginate(
        page=request.GET.get("page", 1), per_page=7)

    context = {
        'table': table,
        'article_groups': articlegroups,
        'filter': noneFilter
    }

    return render(request, 'article/articles.html', context)


@login_required
def analyzeDatasetArticle(request, pk):

    article = get_object_or_404(DatasetArticle, pk=pk)
    try:
        temp_path = get(article.pdf_link)[0]
        create_article_info(article, temp_path, word_count=10)
        create_similarity_score(article, article.article_group)

        messages.success(request, 'Article analyzed successfully!')
    except:
        messages.warning(request, 'PDF file cannot found!')

    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def makeRecommendations(request, pk):

    group = ArticleGroup.objects.get(pk=pk)

    if Recommendation.objects.filter(article_group=group).exists():
        return redirect('group-recommendations', pk)

 
    articles = Article.objects.filter(article_group=pk).values('title', 'keywords')

    if not articles:
        messages.warning(request, 'Please add articles to group!')
        return redirect('group-detail', pk)

    create_related_articles(articles, group)

    create_relation_scores(group)
    messages.success(
        request, f'Your recommendations are ready for {group}')

    return redirect('group-recommendations', pk)


@login_required
def RecommendationPage(request, pk):

    group = ArticleGroup.objects.get(pk=pk)
    recommendations = Recommendation.objects.filter(article_group=pk)

    table = RecommendationsTable(recommendations, order_by=(
        '-relation_score',), exclude=("article_group"))
    RequestConfig(request).configure(table).paginate(
        page=request.GET.get("page", 1), per_page=7)

    context = {
        'table': table,
        'group': group
    }

    return render(request, 'recommendation/recommendation.html', context)


@login_required
def AllRecommendationsPage(request): 

    articlegroups = ArticleGroup.objects.filter(profile=request.user)       
    queryset, noneFilter = modelFilter(Recommendation, request)

    table = RecommendationsTable(queryset, order_by=('-relation_score',))
    RequestConfig(request).configure(table).paginate(
        page=request.GET.get("page", 1), per_page=7)

    context = {
        'table': table,
        'article_groups': articlegroups,
        'filter': noneFilter
    }

    return render(request, 'recommendation/all_recommendations.html', context)
