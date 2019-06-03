from . import Jobs
from django.db import models
from django.contrib.auth.models import User


class Exports(models.Model):
    job = models.ForeignKey(Jobs, on_delete=models.SET_NULL, null=True)
    query_job_id = models.CharField(
        max_length=255, default='00000000-0000-0000-0000-000000000000')
    query_status = models.CharField(max_length=255, default='INITIATED')
    query_completed_at = models.DateTimeField(null=True)
    status = models.CharField(max_length=255, default='PENDING')
    file_name = models.CharField(max_length=255, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'exports'
