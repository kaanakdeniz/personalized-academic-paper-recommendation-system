from django.urls import path

from . import views

urlpatterns = [
    path('', views.homePage, name='main'),

    path('login/', views.loginPage, name='login'),
    path('register/', views.registerPage, name='register'),
    path('logout/', views.logoutUser, name='logout'),

    path('dashboard/', views.dashboardPage, name='home'),

    path('articles/', views.AllArticlesPage, name='articles'),
    path('related-articles/', views.AllRelatedArticlesPage, name='related-articles'),
    path('recommendations/', views.AllRecommendationsPage, name='recommendations'),

    path('article-groups/', views.articleGroupsPage, name='group-list'),
    path('article-group/<str:pk>/',
         views.articleGroupDetailPage, name='group-detail'),
    path('article-group/<str:pk>/delete',
         views.articleGroupDelete, name='group-delete'),
    path('article-group/<str:pk>/recommend',
         views.makeRecommendations, name='group-recommend'),
    path('article-group/<str:pk>/recommendations',
         views.RecommendationPage, name='group-recommendations'),

    path('dataset-article/<str:pk>/',
         views.datasetArticleDetailPage, name='related-detail'),
    path('dataset-article/<str:pk>/delete',
         views.datasetArticleDelete, name='related-delete'),
    path('dataset-article/<str:pk>/update',
         views.updateRelatedArticles, name='related-update'),
    path('dataset-article/<str:pk>/analyze',
         views.analyzeDatasetArticle, name='related-analyze'),

    path('article/<str:pk>/', views.articleDetailPage, name='article-detail'),
    path('article/<str:pk>/delete', views.articleDelete, name='article-delete'),

]
