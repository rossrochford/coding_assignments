from django.db import models
from django.urls import reverse


class Film(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    api_data = models.JSONField()
    people = models.ManyToManyField('Person')
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Film: ' + self.api_data['title']


class Person(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    api_data = models.JSONField()
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Person: ' + self.name

    @property
    def name(self):
        return self.api_data['name']

    def get_detail_url(self, request):
        return request.build_absolute_uri(
            reverse('person-detail', kwargs={'person_id': self.id})
        )
