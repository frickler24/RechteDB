# Generated by Django 2.2.4 on 2019-09-25 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rapp', '0039_auto_20190925_1412'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tbluebersichtafgfs',
            name='geloescht',
            field=models.IntegerField(blank=True, db_column='geloescht', null=True),
        ),
        migrations.AlterField(
            model_name='tbluebersichtafgfs',
            name='name_af_neu',
            field=models.CharField(db_column='name_af_neu', max_length=50, verbose_name='AF Neu'),
        ),
        migrations.AlterUniqueTogether(
            name='tbluebersichtafgfs',
            unique_together={('name_af_neu', 'name_gf_neu')},
        ),
    ]