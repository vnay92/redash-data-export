# Generated by Django 2.2.3 on 2019-09-25 03:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('redash', '0012_jobs_is_scheduled'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobs',
            name='columns_order',
            field=models.CharField(max_length=500, null=True),
        ),
    ]
