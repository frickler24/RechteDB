# Generated by Django 2.1 on 2019-01-26 16:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rapp', '0023_auto_20190126_1538'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='orga_details',
            options={'managed': True, 'ordering': ['id', 'organisation', 'orgID', 'parentOrga', 'fkName'], 'verbose_name': 'Orga-Details', 'verbose_name_plural': '50_Orga - Details'},
        ),
        migrations.AlterModelOptions(
            name='racf_rechte',
            options={'managed': True, 'ordering': ['id', 'profil'], 'verbose_name': 'RACF-Rechte', 'verbose_name_plural': '40_RACF - Berechtigungen'},
        ),
        migrations.AlterModelOptions(
            name='tblafliste',
            options={'managed': True, 'ordering': ['af_name'], 'verbose_name': 'Gültige AF', 'verbose_name_plural': '98_Übersicht gültiger AFen (tbl_AFListe)'},
        ),
        migrations.AlterModelOptions(
            name='tbldb2',
            options={'managed': True, 'ordering': ['id'], 'verbose_name': 'DB2-Berechtigung', 'verbose_name_plural': '30_DB2 - Berechtigungen (Tbl_DB2)'},
        ),
        migrations.AlterModelOptions(
            name='tblgesamt',
            options={'managed': True, 'ordering': ['id'], 'verbose_name': 'Eintrag der Gesamttabelle (tblGesamt)', 'verbose_name_plural': '08_Gesamttabelle Übersicht (tblGesamt)'},
        ),
        migrations.AlterModelOptions(
            name='tblgesamthistorie',
            options={'managed': True, 'verbose_name': 'Historisierter Eintrag der Gesamttabelle (tblGesamtHistorie)', 'verbose_name_plural': '99_Historisierte Einträge der Gesamttabelle (tblGesamtHistorie)'},
        ),
        migrations.AlterModelOptions(
            name='tblorga',
            options={'managed': True, 'ordering': ['team'], 'verbose_name': 'Orga-Information', 'verbose_name_plural': '06_Organisations-Übersicht (tblOrga)'},
        ),
        migrations.AlterModelOptions(
            name='tblplattform',
            options={'managed': True, 'ordering': ['tf_technische_plattform'], 'verbose_name': 'Plattform', 'verbose_name_plural': '07_Plattform-Übersicht (tblPlattform)'},
        ),
        migrations.AlterModelOptions(
            name='tblracfgruppen',
            options={'managed': True, 'ordering': ['group'], 'verbose_name': 'RACF-Berechtigung', 'verbose_name_plural': '40_RACF - Berechtigungen (tbl_DB2)'},
        ),
        migrations.AlterModelOptions(
            name='tblrollehataf',
            options={'managed': True, 'ordering': ['rollenname__rollenname', 'af__af_name'], 'verbose_name': 'Rolle und ihre Arbeitsplatzfunktionen', 'verbose_name_plural': '02_Rollen und ihre Arbeitsplatzfunktionen (tbl_RolleHatAF)'},
        ),
        migrations.AlterModelOptions(
            name='tblrollen',
            options={'managed': True, 'ordering': ['rollenname'], 'verbose_name': 'Rollenliste', 'verbose_name_plural': '03_Rollen-Übersicht (tbl_Rollen)'},
        ),
        migrations.AlterModelOptions(
            name='tblsachgebiete',
            options={'managed': True, 'ordering': ['sachgebiet'], 'verbose_name': 'Sachgebiet', 'verbose_name_plural': '97_Übersicht Sachgebiete (tbl_Sachgebiete)'},
        ),
        migrations.AlterModelOptions(
            name='tblsubsysteme',
            options={'managed': True, 'ordering': ['sgss'], 'verbose_name': 'Subsystem', 'verbose_name_plural': '96_Übersicht Subsysteme (tbl_Subsysteme)'},
        ),
        migrations.AlterModelOptions(
            name='tbluebersichtafgfs',
            options={'managed': True, 'ordering': ['-id'], 'verbose_name': 'Erlaubte AF/GF-Kombination', 'verbose_name_plural': '04_Erlaubte AF/GF-Kombinationen-Übersicht (tblUebersichtAF_GFs)'},
        ),
        migrations.AlterModelOptions(
            name='tbluserhatrolle',
            options={'managed': True, 'ordering': ['userid__name', '-userid__userid', 'schwerpunkt_vertretung', 'rollenname'], 'verbose_name': 'User und Ihre Rollen', 'verbose_name_plural': '01_User und Ihre Rollen (tbl_UserHatRolle)'},
        ),
        migrations.AlterModelOptions(
            name='tbluseridundname',
            options={'managed': True, 'ordering': ['geloescht', 'name', '-userid'], 'verbose_name': 'UserID-Name-Kombination', 'verbose_name_plural': '05_UserID-Name-Übersicht (tblUserIDundName)'},
        ),
    ]
    def apply(self, project_state, schema_editor, collect_sql=False):
        return project_state.clone()

    def unapply(self, project_state, schema_editor, collect_sql=False):
        return project_state.clone()