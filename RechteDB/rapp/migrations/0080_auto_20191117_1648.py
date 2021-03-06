# Generated by Django 2.2.4 on 2019-11-17 16:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rapp', '0079_auto_20191116_1136'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tblgesamt',
            name='tf_beschreibung',
            field=models.CharField(blank=True, db_column='tf_beschreibung', max_length=500, null=True, verbose_name='TF-Beschreibung'),
        ),
        migrations.AlterField(
            model_name='tblgesamthistorie',
            name='tf_beschreibung',
            field=models.CharField(blank=True, db_column='tf_beschreibung', max_length=500, null=True, verbose_name='TF-Beschreibung'),
        ),
        migrations.AlterField(
            model_name='tblrechteamneu',
            name='tf_beschreibung',
            field=models.CharField(blank=True, db_column='tf_beschreibung', max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='tblrechteneuvonimport',
            name='tf_beschreibung',
            field=models.CharField(blank=True, db_column='TF Beschreibung', max_length=500, null=True),
        ),
    ]
