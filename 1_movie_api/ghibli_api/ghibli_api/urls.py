
from django.contrib import admin
from django.urls import path, re_path

from movies.views import movies_list, movie_detail, person_detail


urlpatterns = [
    path('admin/', admin.site.urls),
    path('movies/',  movies_list),
    re_path(r'movie/(?P<movie_id>[a-z0-9\-]{36})', movie_detail, name='movie-detail'),
    re_path(r'person/(?P<person_id>[a-z0-9\-]{36})', person_detail, name='person-detail'),
]
