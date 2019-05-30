from . import Exports
from django.db import models
from django.contrib.auth.models import User


class ExportLogs(models.Model):
    export = models.ForeignKey(Exports, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=255, default='PENDING')
    error_message = models.TextField(default='', null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'export_logs'
