# Generated by Django 2.2.4 on 2019-09-25 14:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rapp', '0045_auto_20190925_1424'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='tblorga',
            unique_together={('team', 'themeneigentuemer')},
        ),
    ]
