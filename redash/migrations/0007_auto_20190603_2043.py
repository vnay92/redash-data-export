# Generated by Django 2.2.1 on 2019-06-03 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('redash', '0006_exports_query_completed_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobs',
            name='end_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='jobs',
            name='start_time',
            field=models.DateTimeField(null=True),
        ),
    ]