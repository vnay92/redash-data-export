# Generated by Django 2.2.1 on 2019-06-03 13:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('redash', '0005_auto_20190530_1817'),
    ]

    operations = [
        migrations.AddField(
            model_name='exports',
            name='query_completed_at',
            field=models.DateTimeField(null=True),
        ),
    ]