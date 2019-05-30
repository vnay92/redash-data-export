# Generated by Django 2.2.1 on 2019-05-30 12:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('redash', '0002_auto_20190528_1403'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExportLogs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(default='PENDING', max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('export', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='redash.Exports')),
            ],
            options={
                'db_table': 'export_logs',
            },
        ),
    ]
