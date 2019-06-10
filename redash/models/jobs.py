from django.db import models
from django.contrib.auth.models import User


class Jobs(models.Model):
    query_id = models.BigIntegerField()
    is_active = models.BooleanField(default=True)
    query_name = models.CharField(max_length=255)
    parameters = models.CharField(max_length=255)
    configured_emails = models.CharField(max_length=255)
    schedule = models.IntegerField(default=4)
    schedule_start_time = models.DateTimeField(auto_now_add=True, null=True)
    schedule_end_time = models.DateTimeField(auto_now_add=True, null=True)
    csv_delimiter = models.CharField(default=',', max_length=2)
    is_excel_required = models.BooleanField(default=False)
    should_be_zipped = models.BooleanField(default=False)
    is_sftp_used = models.BooleanField(default=False)
    sftp_username = models.CharField(max_length=255, null=True)
    sftp_host = models.CharField(max_length=255, null=True)
    sftp_password = models.CharField(max_length=255, null=True)
    sftp_path = models.CharField(max_length=255, null=True)
    is_scheduled = models.BooleanField(default=False)

    added_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, db_column='added_by', related_name='added_by')

    last_edited_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, db_column='last_edited_by', related_name='edited_by')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'jobs'
