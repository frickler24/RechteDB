# Generated by Django 2.2.4 on 2019-09-25 21:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rapp', '0067_auto_20190925_2131'),
    ]

    operations = [
        migrations.AlterField(
            model_name='qryf3rechteneuvonimportduplikatfrei',
            name='hoechste_kritikalitaet_tf_in_af',
            field=models.CharField(blank=True, db_column='hk_tf_in_af', max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='qryf3rechteneuvonimportduplikatfrei',
            name='tf_eigentuemer_org',
            field=models.CharField(blank=True, db_column='tf_eigentuemer_org', max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='qryf3rechteneuvonimportduplikatfrei',
            name='zufallsgenerator',
            field=models.CharField(blank=True, db_column='zufallsgenerator', max_length=8, null=True),
        ),
    ]
