# Generated by Django 2.1 on 2018-08-18 11:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rapp', '0010_auto_20180818_1320'),
    ]

    operations = [
        migrations.AddField(
            model_name='tblrollehataf',
            name='afname',
            field=models.ForeignKey(db_column='AFName', default='Keine AF zugehörig', on_delete=django.db.models.deletion.PROTECT, to='rapp.TblAfliste', to_field='af_name', verbose_name='AF Name'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='tbldb2',
            name='grantor',
            field=models.CharField(db_column='GRANTOR', db_index=True, max_length=15),
        ),
        migrations.AlterField(
            model_name='tbldb2',
            name='table',
            field=models.CharField(db_column='TABLE', db_index=True, max_length=31),
        ),
        migrations.AlterField(
            model_name='tblracfgruppen',
            name='db2_only',
            field=models.IntegerField(blank=True, db_column='DB2-only', db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='tblracfgruppen',
            name='produktion',
            field=models.IntegerField(blank=True, db_column='Produktion', db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='tblracfgruppen',
            name='readonly',
            field=models.IntegerField(blank=True, db_column='Readonly', db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='tblracfgruppen',
            name='stempel',
            field=models.DateTimeField(db_column='Stempel', db_index=True),
        ),
        migrations.AlterField(
            model_name='tblracfgruppen',
            name='test',
            field=models.IntegerField(blank=True, db_column='Test', db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='tblrollehataf',
            name='af',
            field=models.IntegerField(blank=True, db_column='AF', null=True, verbose_name='AF'),
        ),
        migrations.AlterField(
            model_name='tblrollehataf',
            name='rollenname',
            field=models.ForeignKey(db_column='RollenName', on_delete=django.db.models.deletion.PROTECT, to='rapp.TblRollen'),
        ),
    ]