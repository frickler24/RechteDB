# Generated by Django 2.2 on 2019-08-07 17:54

from django.db import migrations
import mdeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('rapp', '0033_manuelle_berechtigung_letzte_aenderung'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='manuelle_berechtigung',
            name='content',
        ),
        migrations.AddField(
            model_name='manuelle_berechtigung',
            name='relativ',
            field=mdeditor.fields.MDTextField(default='Kein Eintrag bis jetzt'),
        ),
        migrations.AddField(
            model_name='manuelle_berechtigung',
            name='statisch',
            field=mdeditor.fields.MDTextField(default='Kein Eintrag bis jetzt'),
        ),
    ]
