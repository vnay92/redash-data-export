# Generated by Django 2.2.1 on 2019-05-30 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('redash', '0004_exportlogs_error_message'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exportlogs',
            name='error_message',
            field=models.TextField(default='', null=True),
        ),
    ]
