# Generated by Django 2.2.4 on 2019-11-09 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rapp', '0074_auto_20191109_1554'),
    ]

    operations = [
        migrations.AddField(
            model_name='tblrechteamneu',
            name='af_beschreibung',
            field=models.TextField(blank=True, default='', max_length=2000, null=True),
        ),
        migrations.AlterField(
            model_name='tblrechteneuvonimport',
            name='af_beschreibung',
            field=models.CharField(blank=True, db_column='AF Beschreibung', max_length=2000, null=True),
        ),
    ]
