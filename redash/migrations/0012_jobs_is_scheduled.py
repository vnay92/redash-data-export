# Generated by Django 2.2.1 on 2019-06-10 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('redash', '0011_auto_20190608_0943'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobs',
            name='is_scheduled',
            field=models.BooleanField(default=False),
        ),
    ]
