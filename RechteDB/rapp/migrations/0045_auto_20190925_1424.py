# Generated by Django 2.2.4 on 2019-09-25 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rapp', '0044_auto_20190925_1421'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tblorga',
            name='themeneigentuemer',
            field=models.CharField(db_column='themeneigentuemer', max_length=64),
        ),
    ]