from django.contrib import admin

from movies.models import Film, Person

admin.site.register(Film)
admin.site.register(Person)
