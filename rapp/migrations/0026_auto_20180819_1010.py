# Generated by Django 2.1 on 2018-08-19 08:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rapp', '0024_auto_20180819_0000'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tblrechteamneu',
            name='id',
            field=models.AutoField(db_column='ID', primary_key=True, serialize=False),
        ),
    ]
