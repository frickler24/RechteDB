# Generated by Django 2.2.4 on 2020-02-16 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rapp', '0090_letzter_import_zi_orga'),
    ]

    operations = [
        migrations.AddField(
            model_name='tblplattform',
            name='geloescht',
            field=models.IntegerField(blank=True, null=True, verbose_name='gelöscht'),
        ),
    ]
