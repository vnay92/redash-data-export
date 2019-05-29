from django.contrib import admin
from django.contrib.admin import AdminSite

# Register your models here.
from redash.models.jobs import Jobs
from redash.models.exports import Exports

admin.site.register(Jobs)
admin.site.register(Exports)
