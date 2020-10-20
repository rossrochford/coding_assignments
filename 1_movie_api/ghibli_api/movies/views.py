from django.http import JsonResponse
from django.urls import reverse

from .models import Film


FILM_KEYS_TO_REMOVE = ['people', 'species', 'locations', 'vehicles']
PERSON_KEYS_TO_REMOTE = ['films', 'species']


def _get_film_api_entry(request, movie_obj):
    # modify data from Ghibli API slightly
    data = movie_obj.api_data

    for key in FILM_KEYS_TO_REMOVE:
        if key in data:
            del data[key]

    data['url'] = reverse('movie-detail', kwargs={'movie_id': movie_obj.id})
    # what should 'people' contain? name? url? json data?
    data['people'] = [p.name for p in movie_obj.people.all()]

    return data


def movies_list(request):

    movies = Film.objects.prefetch_related('people')

    results = [
        _get_film_api_entry(request, movie_obj) for movie_obj in movies
    ]

    return JsonResponse({'movies': results})


def movie_detail(request, movie_id):
    raise NotImplementedError


def person_detail(request, person_id):
    raise NotImplementedError
