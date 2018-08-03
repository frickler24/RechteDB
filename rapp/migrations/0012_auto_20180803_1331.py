# Generated by Django 2.0.7 on 2018-08-03 11:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rapp', '0011_auto_20180803_1323'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tblafliste',
            options={'managed': False, 'ordering': ['af_name'], 'verbose_name': 'Gültige AF', 'verbose_name_plural': 'Übersicht gültiger AFen (tbl_AFListe)'},
        ),
        migrations.AlterModelOptions(
            name='tblrollehataf',
            options={'managed': False, 'ordering': ['rollenname__rollenname', 'af__af_name'], 'verbose_name': 'Rolle und ihre Arbeitsplatzfunktionen', 'verbose_name_plural': 'Rollen und ihre Arbeitsplatzfunktionen (tbl_RolleHatAF)'},
        ),
        migrations.AlterField(
            model_name='tblgesamthistorie',
            name='id_alt',
            field=models.ForeignKey(db_column='ID-alt', on_delete=django.db.models.deletion.PROTECT, to='rapp.TblGesamt'),
        ),
    ]
