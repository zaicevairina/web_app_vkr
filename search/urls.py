from search.views import search_page, same_article
from django.urls import path

urlpatterns = [
    path('', search_page, name='search'),
    path('same_article', same_article, name='same_article'),
]