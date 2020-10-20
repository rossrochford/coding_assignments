from collections import defaultdict
import datetime
import re

from django.core.management.base import BaseCommand
import pytz
import requests

from movies.models import Film, Person


FILMS_URL = 'https://ghibliapi.herokuapp.com/films/'
PEOPLE_URL = 'https://ghibliapi.herokuapp.com/people/'

FILM_ID_REGEX = re.escape('https://ghibliapi.herokuapp.com/films/') + r'(?P<film_id>[a-z0-9\-]{36})'

# https://ghibliapi.herokuapp.com/films/0440483e-ca0e-4120-8c50-4c8cd9b965d6


FILM_RESPONSE = {
    'id': '0440483e-ca0e-4120-8c50-4c8cd9b965d6',
    'title': 'Princess Mononoke',
    'description': 'Ashhis conflict.',
    'director': 'Hayao Miyazaki',
    'producer': 'Toshio Suzuki',
    'release_date': '1997',
    'rt_score': '92',
    'people': ['https://ghibliapi.herokuapp.com/people/116bfe1b-3ba8-4fa0-8f72-88537a493cb9'],
    'species': ['https://ghibliapi.herokuapp.com/species/f25fa661-3073-414d-968a-ab062e3065f7'],
    'locations': ['https://ghibliapi.herokuapp.com/locations/'],
    'vehicles': ['https://ghibliapi.herokuapp.com/vehicles/'],
    'url': 'https://ghibliapi.herokuapp.com/films/0440483e-ca0e-4120-8c50-4c8cd9b965d6',
    'length': None
}

'''
# film response:

{
    'id': '2baf70d1-42bb-4437-b551-e5fed5a87abe', 
    'title': 'Castle in the Sky', 
    'description': "Thworld.", 
    'director': 'Hayao Miyazaki', 
    'producer': 'Isao Takahata', 
    'release_date': '1986', 
    'rt_score': '95', 
    'people': ['https://ghibliapi.herokuapp.com/people/'], 
    'species': ['https://ghibliapi.herokuapp.com/species/af3910a6-429f-4c74-9ad5-dfe1c4aa04f2'], 
    'locations': ['https://ghibliapi.herokuapp.com/locations/'], 
    'vehicles': ['https://ghibliapi.herokuapp.com/vehicles/'], 
    'url': 'https://ghibliapi.herokuapp.com/films/2baf70d1-42bb-4437-b551-e5fed5a87abe'
}

# people response:

{
    'id': 'ba924631-068e-4436-b6de-f3283fa848f0', 
    'name': 'Ashitaka', 
    'gender': 'Male', 
    'age': 'late teens', 
    'eye_color': 'Brown', 
    'hair_color': 'Brown', 
    'films': ['https://ghibliapi.herokuapp.com/films/0440483e-ca0e-4120-8c50-4c8cd9b965d6'], 
    'species': 'https://ghibliapi.herokuapp.com/species/af3910a6-429f-4c74-9ad5-dfe1c4aa04f2', 
    'url': 'https://ghibliapi.herokuapp.com/people/ba924631-068e-4436-b6de-f3283fa848f0'
}
'''


def get_utc_now():
    return datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)


def _get_film_data():
    resp = requests.get(FILMS_URL)
    if resp.status_code != 200:
        return None
    return resp.json()


def _get_people_data():
    resp = requests.get(PEOPLE_URL)
    if resp.status_code != 200:
        return None
    return resp.json()


def _refresh_films(films_json_data):
    now = get_utc_now()
    film_data = {di['id']: di for di in films_json_data}

    existing_films = Film.objects.filter(id__in=film_data.keys())
    existing_film_ids = [obj.id for obj in existing_films]
    new_film_ids = [id for id in film_data.keys() if id not in existing_film_ids]

    # add any new films
    if new_film_ids:
        Film.objects.bulk_create([
            Film(id=id, api_data=film_data[id], modified=now)
            for id in new_film_ids
        ])

    # update existing films, if modified > 7 days ago
    week_ago = now - datetime.timedelta(days=7)
    films_for_update = Film.objects.filter(
        modified__lt=week_ago, id__in=existing_film_ids
    )
    if films_for_update:
        for film_obj in films_for_update:
            film_obj.api_data = film_data[film_obj.id]
            film_obj.modified = now
        Film.objects.bulk_update(films_for_update, ['api_data', 'modified'])

    # remove any films that weren't present in the API response
    Film.objects.exclude(id__in=film_data.keys()).delete()


def _refresh_people(people_json_data):
    now = get_utc_now()
    people_data = {di['id']: di for di in people_json_data}

    existing_people = Person.objects.filter(id__in=people_data.keys())
    existing_people_ids = [obj.id for obj in existing_people]
    new_people_ids = [id for id in people_data.keys() if id not in existing_people_ids]

    # add any new people
    if new_people_ids:
        Person.objects.bulk_create([
            Person(id=id, api_data=people_data[id], modified=now)
            for id in new_people_ids
        ])

    # update existing people, if modified > 7 days ago
    week_ago = now - datetime.timedelta(days=7)
    people_for_update = Person.objects.filter(
        modified__lt=week_ago, id__in=existing_people_ids
    )
    if people_for_update:
        for person_obj in people_for_update:
            person_obj.api_data = people_data[person_obj.id]
            person_obj.modified = now
        Person.objects.bulk_update(people_for_update, ['api_data', 'modified'])

    # remove any people that weren't present in the API response
    Person.objects.exclude(id__in=people_data.keys()).delete()

    # collect person <--> film relationships by id
    people_by_film_id = defaultdict(list)
    for person_id, person_dict in people_data.items():
        for film_url in person_dict['films']:
            regex_match = re.search(FILM_ID_REGEX, film_url)
            if regex_match is None:
                continue
            film_id = regex_match.groupdict()['film_id']
            people_by_film_id[film_id].append(person_id)

    films = {obj.id: obj for obj in Film.objects.all()}
    people = {obj.id: obj for obj in Person.objects.all()}

    # add people to films in database, note: django will not add duplicates
    for film_id, people_ids in people_by_film_id.items():
        ppl = [people[id] for id in people_ids]
        films[film_id].people.add(*ppl)


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        film_data = _get_film_data()
        if film_data is None:
            return
        _refresh_films(film_data)

        people_data = _get_people_data()
        if people_data is None:
            return
        _refresh_people(people_data)
