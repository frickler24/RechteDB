# Generated by Django 3.0.4 on 2020-04-28 20:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rapp', '0091_tblplattform_geloescht'),
    ]

    operations = [
        migrations.DeleteModel(
            name='kanndaswegTblRacfGruppen',
        ),
        migrations.AddField(
            model_name='tblrechteamneu',
            name='organisation',
            field=models.CharField(default='', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tblrechteneuvonimport',
            name='organisation',
            field=models.CharField(default='Fehler!!!', max_length=20),
        ),
    ]
