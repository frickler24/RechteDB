# Generated by Django 2.2.4 on 2019-12-03 19:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rapp', '0081_auto_20191118_1926'),
    ]

    operations = [
        migrations.AddField(
            model_name='tblorga',
            name='teamliste',
            field=models.CharField(blank=True, default=None, max_length=400, null=True),
        ),
    ]