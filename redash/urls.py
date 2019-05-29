from django.urls import path

from redash.views import job
from redash.views import export

urlpatterns = [
    path('jobs/all/', job.all, name='alljobs'),
    path('jobs/new/', job.new, name='newjob'),
    path('jobs/create/', job.create, name='createjob'),
    path('jobs/edit/<int:id>/', job.edit, name='editjob'),
    path('jobs/save/<int:id>/', job.save, name='savejob'),
    path('jobs/delete/<int:id>/', job.delete, name='deletejob'),

    path('exports/all/', export.all, name='allexports'),
    path('exports/edit/<int:id>/', export.edit, name='editexport'),
    path('exports/save/<int:id>/', export.save, name='saveexport'),
    path('exports/delete/<int:id>/', export.delete, name='deleteexport'),
]
