# Generated by Django 2.1 on 2019-02-23 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rapp', '0025_letzter_import'),
    ]

    operations = [
        migrations.AddField(
            model_name='letzter_import',
            name='schritt',
            field=models.IntegerField(default=0),
        ),
    ]