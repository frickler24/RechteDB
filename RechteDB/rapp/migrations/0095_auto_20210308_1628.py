# Generated by Django 3.0.4 on 2021-03-08 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rapp', '0094_add_iiq_organisation_20200503_1031'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tblrechteamneu',
            name='organisation',
        ),
        migrations.RemoveField(
            model_name='tblrechteneuvonimport',
            name='organisation',
        ),
        migrations.AlterField(
            model_name='tbluseridundname',
            name='gruppe',
            field=models.CharField(db_column='gruppe', db_index=True, max_length=50),
        ),
    ]