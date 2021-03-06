# Generated by Django 2.2.4 on 2019-09-25 20:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rapp', '0056_auto_20190925_2040'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tbluebersichtafgfs',
            name='name_gf_neu',
            field=models.CharField(db_column='name_gf_neu', db_index=True, max_length=50, verbose_name='GF Neu'),
        ),
        migrations.AlterUniqueTogether(
            name='tbluebersichtafgfs',
            unique_together={('name_af_neu', 'name_gf_neu')},
        ),
    ]
