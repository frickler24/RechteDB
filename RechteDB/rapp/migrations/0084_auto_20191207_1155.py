# Generated by Django 2.2.4 on 2019-12-07 11:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rapp', '0083_auto_20191207_1144'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tblorga',
            name='freies_team',
            field=models.CharField(blank=True, default=None, max_length=4000, null=True),
        ),
    ]
