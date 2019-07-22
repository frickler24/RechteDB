from django.urls import reverse, resolve
from django.test import TestCase

from datetime import datetime, timedelta
from django.utils import timezone
# from django.core.files.base import ContentFile
import re
from ..anmeldung import Anmeldung
from ..views import home
from ..models import TblOrga, TblUebersichtAfGfs, TblUserIDundName, TblPlattform, TblGesamt, \
					 TblAfliste, TblUserhatrolle, TblRollehataf, TblRollen, Tblrechteneuvonimport
from ..view_import import patch_datum, neuer_import

class HomeTests(TestCase):
	def setup(self):
		Setup_database()

	# Sind die einzelnen Hsuptseiten erreichbar?
	# Generell: Funktioniert irgend etwas?
	def test_something_is_running(self):
		self.assertTrue(True)

	# Funktioniert die Einstiegsseite?
	def test_home_view_status_code(self):
		url = reverse('home')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)

	def test_home_url_resolves_home_view(self):
		view = resolve('/rapp/')
		self.assertEqual(view.func, home)

	def test_home_url_gets_info_screen(self):
		# Alle Daten erscheinen auf der Übersichtsseite
		url = reverse('home')
		self.response = self.client.get(url)
		self.assertEqual(self.response.status_code, 200)
		self.assertContains(self.response, 'Statistik über die RApp-Inhalte:', 1)
		self.assertContains(self.response, 'Status Stored Procedures:', 1)
		self.assertContains(self.response, 'Stand letzter Import:', 1)
		self.assertContains(self.response, 'Administrierte Berechtigungen:', 1)
		self.assertContains(self.response, 'Aktive Rechte:', 1)
		self.assertContains(self.response, 'Administrierte UserIDs:', 1)
		self.assertContains(self.response, 'Aktive UserIDs:', 1)
		self.assertContains(self.response, 'UserIDs von AI-BA:', 1)
		self.assertContains(self.response, 'Vorhandene Teams:', 1)
		self.assertContains(self.response, 'Bekannte Plattformen:', 1)
		self.assertContains(self.response, 'Anwender der RApp:', 1)
		self.assertContains(self.response, 'Aktuelle TFen in AI-BA:', 1)
		self.assertContains(self.response, '/static/admin/img/icon-yes.svg', 1)

class AdminPageTests(TestCase):
	# Erreichbarkeit der Admin-Seiten (Simpel-Modus)
	def test_adminrapp_view_status_code(self):
		url = reverse('home')[:-5] + 'adminrapp'
		response = self.client.get(url)
		self.assertEqual(response.status_code, 301)

	def test_adminrapp_l1_view_status_code(self):
		url = reverse('home')[:-5] + 'adminrapp/tbluserhatrolle'
		response = self.client.get(url)
		self.assertEqual(response.status_code, 301)

	def test_adminrapp_l2_view_status_code(self):
		url = reverse('home')[:-5] + 'adminrapp/tblrollehataf'
		response = self.client.get(url)
		self.assertEqual(response.status_code, 301)

	def test_adminrapp_l3_view_status_code(self):
		url = reverse('home')[:-5] + 'adminrapp/tblrollen'
		response = self.client.get(url)
		self.assertEqual(response.status_code, 301)

	def test_adminrapp_l4_view_status_code(self):
		url = reverse('home')[:-5] + 'adminrapp/tbluebersichtafgfs'
		response = self.client.get(url)
		self.assertEqual(response.status_code, 301)

	def test_adminrapp_l5_view_status_code(self):
		url = reverse('home')[:-5] + 'adminrapp/tbluseridundname'
		response = self.client.get(url)
		self.assertEqual(response.status_code, 301)

	def test_adminrapp_l6_view_status_code(self):
		url = reverse('home')[:-5] + 'adminrapp/tblorga'
		response = self.client.get(url)
		self.assertEqual(response.status_code, 301)

	def test_adminrapp_l7_view_status_code(self):
		url = reverse('home')[:-5] + 'adminrapp/tblplattform'
		response = self.client.get(url)
		self.assertEqual(response.status_code, 301)

	def test_adminrapp_l8_view_status_code(self):
		url = reverse('home')[:-5] + 'adminrapp/tblgesamt'
		response = self.client.get(url)
		self.assertEqual(response.status_code, 301)

	def test_adminrapp_l9_view_status_code(self):
		url = reverse('home')[:-5] + 'adminrapp/tblsubsysteme'
		response = self.client.get(url)
		self.assertEqual(response.status_code, 301)

	def test_adminrapp_l10_view_status_code(self):
		url = reverse('home')[:-5] + 'adminrapp/tblsachgebiete'
		response = self.client.get(url)
		self.assertEqual(response.status_code, 301)

	def test_adminrapp_l11_view_status_code(self):
		url = reverse('home')[:-5] + 'adminrapp/tbldb2'
		response = self.client.get(url)
		self.assertEqual(response.status_code, 301)

	""" Diese Admin-Seite ist derzeit nicht aktiv
	def test_adminrapp_l12_view_status_code(self):
		url = reverse('home')[:-5] + 'adminrapp/tblracfgruppen'
		response = self.client.get(url)
		self.assertEqual(response.status_code, 301)
	"""

	def test_adminrapp_l13_view_status_code(self):
		url = reverse('home')[:-5] + 'adminrapp/tblafliste'
		response = self.client.get(url)
		self.assertEqual(response.status_code, 301)

	def test_adminrapp_l14_view_status_code(self):
		url = reverse('home')[:-5] + 'adminrapp/tblgesamthistorie'
		response = self.client.get(url)
		self.assertEqual(response.status_code, 301)


	def test_adminrapp_l15_view_status_code(self):
		url = reverse('home')[:-5] + 'adminrapp/racf_rechte'
		response = self.client.get(url)
		self.assertEqual(response.status_code, 301)


	def test_adminrapp_l16_view_status_code(self):
		url = reverse('home')[:-5] + 'adminrapp/orga_details'
		response = self.client.get(url)
		self.assertEqual(response.status_code, 301)


class GesamtlisteTests(TestCase):
	# Funktioniert die Gesamtliste?
	def setUp(self):
		Anmeldung(self.client.login)
		Setup_database()

		for i in range (100):
			TblOrga.objects.create(
				team = 'Django-Team-{}'.format(i),
				themeneigentuemer = 'Ihmchen_{}'.format(2 * i)
			)

		TblUebersichtAfGfs.objects.create(
			name_gf_neu =			'rvg_00458_neueGF mit echt mehr Zeichen als üblich',
			name_af_neu =			'rva_00458_neue_AF auch mit mehr Zeichen als üblich',
			kommentar =				'Kein Kommentar',
			zielperson =			'Lutz',
			af_text =				'Das ist der AF-normaltext',
			gf_text = 				'Das ist der AF-normaltext',
			af_langtext = 			'Das ist der AF-Laaaaaaaaaaaaaaaaaaaaaaaaaaaaaaang-Text',
			af_ausschlussgruppen =	'Das soll niemand außer mir bekommen!!!',
			af_einschlussgruppen =	'das soll die ganze Welt erhalten können',
			af_sonstige_vergabehinweise = 'Keine Hinweise',
			geloescht =				False,
			kannweg = 				False,
			modelliert = 			timezone.now(),
		)
		TblUebersichtAfGfs.objects.create(
			name_gf_neu =			'rvg_00500_neueGF mit echt mehr Zeichen als üblich',
			name_af_neu =			'rva_00500_neue_AF auch mit mehr Zeichen als üblich',
		)
		TblUebersichtAfGfs.objects.create(
			name_gf_neu =			'rvg_00380_neueGF mit echt mehr Zeichen als üblich',
			name_af_neu =			'rva_00380_neue_AF auch mit mehr Zeichen als üblich',
		)

		for i in range(10, 20):
			TblUserIDundName.objects.create(
				userid = 			'xv100{}'.format(i),
				name = 				'User_xv100{}'.format(i),
				orga = 				TblOrga.objects.get(team = 'Django-Team-{}'.format(i)),
				zi_organisation =	'AI-BA',
				geloescht = 		False,
				abteilung = 		'ZI-AI-BA',
				gruppe = 			'ZI-AI-BA-PS',
			)

		TblPlattform.objects.create(tf_technische_plattform = 'RACFP')

		TblGesamt.objects.create(
			userid_name = 			TblUserIDundName.objects.get(userid = 'xv10011'),
			tf = 					'Die superlange schnuckelige TF',
			tf_beschreibung = 		'Die superlange schnuckelige TF-Beschreibung',
			enthalten_in_af = 		'rva_00458_neue_AF auch mit mehr Zeichen als üblich',
			modell = 				TblUebersichtAfGfs.objects.get(name_af_neu='rva_00458_neue_AF auch mit mehr Zeichen als üblich',
																   name_gf_neu='rvg_00458_neueGF mit echt mehr Zeichen als üblich'),
			tf_kritikalitaet = 		'Superkritisch sich ist das auch schon zu lang',
			tf_eigentuemer_org = 	'Keine Ahnung Org',
			plattform = 			TblPlattform.objects.get(tf_technische_plattform = 'RACFP'),
			gf = 					'rvg_00458_neueGF mit echt mehr Zeichen als üblich',
			vip_kennzeichen = 		'',
			zufallsgenerator = 		'',
			af_gueltig_ab = 		timezone.now() - timedelta(days=365),
			af_gueltig_bis = 		timezone.now() + timedelta(days=365),
			direct_connect = 		'no direct connect',
			hoechste_kritikalitaet_tf_in_af = 'u',
			gf_beschreibung = 		'Die superlange, mindestens 250 Zeichen umfassende GF-Beschreibung. Hier könnte man auch mal nach CRLF suchen',
			af_zuweisungsdatum = 	timezone.now() - timedelta(days=200),
			datum = 				timezone.now() - timedelta(days=500),
			geloescht = 			False,
			gefunden = 				True,
			wiedergefunden = 		timezone.now(),
			geaendert = 			False,
			neueaf = 				'',
			nicht_ai = 				False,
			patchdatum = 			None,
			wertmodellvorpatch =	'Hier kommt nix rein',
			loeschdatum = 			None,
			letzte_aenderung =		None
		)

		TblGesamt.objects.create(
			userid_name = 			TblUserIDundName.objects.get(userid = 'xv10012'),
			tf = 					'Die superlange schnuckelige TF2',
			tf_beschreibung = 		'Die superlange schnuckelige TF-Beschreibung',
			enthalten_in_af = 		'rva_00458_neue_AF auch mit mehr Zeichen als üblich',
			modell = 				TblUebersichtAfGfs.objects.get(name_af_neu='rva_00458_neue_AF auch mit mehr Zeichen als üblich',
																   name_gf_neu='rvg_00458_neueGF mit echt mehr Zeichen als üblich'),
			tf_kritikalitaet = 		'Superkritisch sich ist das auch schon zu lang',
			tf_eigentuemer_org = 	'Keine Ahnung Org',
			plattform = 			TblPlattform.objects.get(tf_technische_plattform = 'RACFP'),
			gf = 					'rvg_00458_neueGF mit echt mehr Zeichen als üblich',
			vip_kennzeichen = 		'',
			zufallsgenerator = 		'',
			af_gueltig_ab = 		timezone.now() - timedelta(days=365),
			af_gueltig_bis = 		timezone.now() + timedelta(days=365),
			direct_connect = 		'no direct connect',
			hoechste_kritikalitaet_tf_in_af = 'u',
			gf_beschreibung = 		'Die superlange, mindestens 250 Zeichen umfassende GF-Beschreibung. Hier könnte man auch mal nach CRLF suchen',
			af_zuweisungsdatum = 	timezone.now() - timedelta(days=200),
			datum = 				timezone.now() - timedelta(days=500),
			geloescht = 			False,
			gefunden = 				True,
			wiedergefunden = 		timezone.now(),
			geaendert = 			False,
			neueaf = 				'',
			nicht_ai = 				False,
			patchdatum = 			None,
			wertmodellvorpatch =	'Hier kommt nix rein',
			loeschdatum = 			None,
			letzte_aenderung =		None
		)


	def test_gesamtliste_view_status_code(self):
		url = reverse('gesamtliste')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)

	def test_gesamtliste_view_not_found_status_code(self):
		url = reverse('gesamt-detail', kwargs={'pk': 99999999})
		response = self.client.get(url)
		self.assertEqual(response.status_code, 404)

	# Kann das zweite Element direkt adressiert werden?
	def test_gesamtliste_view_success_status_code(self):
		url = reverse('gesamt-detail', kwargs={'pk': TblGesamt.objects.get(tf = 'Die superlange schnuckelige TF2').id})
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)

class TeamListTests(TestCase):
	def setUp(self):
		Anmeldung(self.client.login)
		Setup_database()
	# Geht die Team-Liste?
	# Ist die Seite da?
	# ToDo: Beim Test der Teamliste fehlen noch die drei subpanels. Aber evtl. fällt die gesamte Liste weg
	def test_teamlist_view_status_code(self):
		url = reverse('teamliste')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
class CreateTeamTests(TestCase):
	# Geht die Team-Liste inhaltlich?
	def setUp(self):
		Anmeldung(self.client.login)
		Setup_database()
		TblOrga.objects.create(team='MeinTeam', themeneigentuemer='Icke')

	def test_create_team_view_success_status_code(self):
		url = reverse('team-create')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
	"""
	def test_create_team_url_resolves_new_topic_view(self):
		view = resolve('/teamliste/create/')
		self.assertEqual(view.func, TblOrgaCreate.as_view)
	"""

	def test_create_team_view_contains_link_back_to_board_topics_view(self):
		new_team_url = reverse('team-create')
		teamlist_url = reverse('teamliste')
		response = self.client.get(new_team_url)
		self.assertContains(response, 'href="{0}"'.format(teamlist_url))

class UserListTests(TestCase):
	def setUp(self):
		Anmeldung(self.client.login)
		Setup_database()
	# Geht die User-Liste?
	# Ist die Seite da?
	def test_userlist_view_status_code(self):
		url = reverse('userliste')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
class CreateUserTests(TestCase):
	# Geht die User-Liste inhaltlich?
	def setUp(self):
		Anmeldung(self.client.login)
		Setup_database()
		TblOrga.objects.create(team = 'Django-Team', themeneigentuemer = 'Ihmchen')

		TblUebersichtAfGfs.objects.create(
			name_gf_neu =			'rvg_00458_neueGF mit echt mehr Zeichen als üblich',
			name_af_neu =			'rva_00458_neue_AF auch mit mehr Zeichen als üblich',
			kommentar =				'Kein Kommentar',
			zielperson =			'Lutz',
			af_text =				'Das ist der AF-normaltext',
			gf_text = 				'Das ist der GF-normaltext',
			af_langtext = 			'Das ist der AF-Laaaaaaaaaaaaaaaaaaaaaaaaaaaaaaang-Text',
			af_ausschlussgruppen =	'Das soll niemand außer mir bekommen!!!',
			af_einschlussgruppen =	'das soll die ganze Welt erhalten können',
			af_sonstige_vergabehinweise = 'Keine Hinweise',
			geloescht =				False,
			kannweg = 				False,
			modelliert = 			timezone.now(),
		)
		TblUebersichtAfGfs.objects.create(
			name_gf_neu =			'rvg_00500_neueAF mit echt mehr Zeichen als üblich',
			name_af_neu =			'rva_00500_neue_AF auch mit mehr Zeichen als üblich',
		)
		TblUebersichtAfGfs.objects.create(
			name_gf_neu =			'rvg_00380_neueAF mit echt mehr Zeichen als üblich',
			name_af_neu =			'rva_00380_neue_AF auch mit mehr Zeichen als üblich',
		)

		TblUserIDundName.objects.create(
			userid = 			'xv10010',
			name = 				'User_xv10010',
			orga = 				TblOrga.objects.get(team = 'Django-Team'),
			zi_organisation =	'AI-BA',
			geloescht = 		False,
			abteilung = 		'ZI-AI-BA',
			gruppe = 			'ZI-AI-BA-PS',
		)

	def test_create_user_view_success_status_code(self):
		url = reverse('user-create')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)

	def test_create_user_view_contains_link_back_to_board_topics_view(self):
		new_user_url = reverse('user-create')
		userlist_url = reverse('userliste')
		response = self.client.get(new_user_url)
		self.assertContains(response, 'href="{0}"'.format(userlist_url))

class PanelTests(TestCase):
	# Suche-/Filterpanel. Das wird mal die Hauptseite für Reports
	def setUp(self):
		Anmeldung(self.client.login)
		Setup_database()

		TblOrga.objects.create(
			team = 'Django-Team-01',
			themeneigentuemer = 'Ihmchen_01'
		)

		TblUebersichtAfGfs.objects.create(
			name_gf_neu =			'rvg_00458_neueGF mit echt mehr Zeichen als üblich',
			name_af_neu =			'rva_00458_neue_AF auch mit mehr Zeichen als üblich',
			kommentar =				'Kein Kommentar',
			zielperson =			'Lutz',
			af_text =				'Das ist der AF-normaltext',
			gf_text = 				'Das ist der GF-normaltext',
			af_langtext = 			'Das ist der AF-Laaaaaaaaaaaaaaaaaaaaaaaaaaaaaaang-Text',
			af_ausschlussgruppen =	'Das soll niemand außer mir bekommen!!!',
			af_einschlussgruppen =	'das soll die ganze Welt erhalten können',
			af_sonstige_vergabehinweise = 'Keine Hinweise',
			geloescht =				False,
			kannweg = 				False,
			modelliert = 			timezone.now(),
		)
		TblUebersichtAfGfs.objects.create(
			name_gf_neu =			'rvg_00500_neueAF mit echt mehr Zeichen als üblich',
			name_af_neu =			'rva_00500_neue_AF auch mit mehr Zeichen als üblich',
		)
		TblUebersichtAfGfs.objects.create(
			name_gf_neu =			'rvg_00380_neueAF mit echt mehr Zeichen als üblich',
			name_af_neu =			'rva_00380_neue_AF auch mit mehr Zeichen als üblich',
		)

		TblUserIDundName.objects.create(
			userid = 			'xv10099',
			name = 				'User_xv10099',
			orga = 				TblOrga.objects.get(team = 'Django-Team-01'),
			zi_organisation =	'AI-BA',
			geloescht = 		False,
			abteilung = 		'ZI-AI-BA',
			gruppe = 			'ZI-AI-BA-PS',
		)

		TblPlattform.objects.create(tf_technische_plattform = 'RACFP')

		TblGesamt.objects.create(
			userid_name = 			TblUserIDundName.objects.get(userid = 'xv10099'),
			tf = 					'Die superlange schnuckelige TF',
			tf_beschreibung = 		'Die superlange schnuckelige TF-Beschreibung',
			enthalten_in_af = 		'rva_00458_neue_AF auch mit mehr Zeichen als üblich',
			modell = 				TblUebersichtAfGfs.objects.get(name_af_neu='rva_00380_neue_AF auch mit mehr Zeichen als üblich',
																   name_gf_neu='rvg_00380_neueAF mit echt mehr Zeichen als üblich'),
			tf_kritikalitaet = 		'Superkritisch sich ist das auch schon zu lang',
			tf_eigentuemer_org = 	'Keine Ahnung Org',
			plattform = 			TblPlattform.objects.get(tf_technische_plattform = 'RACFP'),
			gf = 					'rvg_00380_neueGF mit echt mehr Zeichen als üblich',
			vip_kennzeichen = 		'',
			zufallsgenerator = 		'',
			af_gueltig_ab = 		timezone.now() - timedelta(days=365),
			af_gueltig_bis = 		timezone.now() + timedelta(days=365),
			direct_connect = 		'no direct connect',
			hoechste_kritikalitaet_tf_in_af = 'u',
			gf_beschreibung = 		'Die superlange, mindestens 250 Zeichen umfassende GF-Beschreibung. Hier könnte man auch mal nach CRLF suchen',
			af_zuweisungsdatum = 	timezone.now() - timedelta(days=200),
			datum = 				timezone.now() - timedelta(days=500),
			geloescht = 			False,
			gefunden = 				True,
			wiedergefunden = 		timezone.now(),
			geaendert = 			False,
			neueaf = 				'',
			nicht_ai = 				False,
			patchdatum = 			None,
			wertmodellvorpatch =	'Hier kommt nix rein',
			loeschdatum = 			None,
			letzte_aenderung =		None
		)

		TblGesamt.objects.create(
			userid_name = 			TblUserIDundName.objects.get(userid = 'xv10099'),
			tf = 					'Die superlange schnuckelige TF2',
			tf_beschreibung = 		'Die superlange schnuckelige TF-Beschreibung',
			enthalten_in_af = 		'rva_00458_neue_AF auch mit mehr Zeichen als üblich',
			modell = 				TblUebersichtAfGfs.objects.get(name_af_neu='rva_00458_neue_AF auch mit mehr Zeichen als üblich',
																   name_gf_neu='rvg_00458_neueGF mit echt mehr Zeichen als üblich'),
			tf_kritikalitaet = 		'Superkritisch sich ist das auch schon zu lang',
			tf_eigentuemer_org = 	'Keine Ahnung Org',
			plattform = 			TblPlattform.objects.get(tf_technische_plattform = 'RACFP'),
			gf = 					'rvg_00458_neueAF mit echt mehr Zeichen als üblich',
			vip_kennzeichen = 		'',
			zufallsgenerator = 		'',
			af_gueltig_ab = 		timezone.now() - timedelta(days=365),
			af_gueltig_bis = 		timezone.now() + timedelta(days=365),
			direct_connect = 		'no direct connect',
			hoechste_kritikalitaet_tf_in_af = 'u',
			gf_beschreibung = 		'Die superlange, mindestens 250 Zeichen umfassende GF-Beschreibung. Hier könnte man auch mal nach CRLF suchen',
			af_zuweisungsdatum = 	timezone.now() - timedelta(days=200),
			datum = 				timezone.now() - timedelta(days=500),
			geloescht = 			False,
			gefunden = 				True,
			wiedergefunden = 		timezone.now(),
			geaendert = 			False,
			neueaf = 				'',
			nicht_ai = 				False,
			patchdatum = 			None,
			wertmodellvorpatch =	'Hier kommt nix rein',
			loeschdatum = 			None,
			letzte_aenderung =		None
		)

	# Ist die Seite da?
	def test_panel_view_status_code(self):
		url = reverse('panel')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)

	def test_panel_view_with_valid_selection_status_code(self):
		url = '{0}{1}'.format(reverse('panel'), '?geloescht=3&userid_name__zi_organisation=ai-ba')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "User_xv10099")

	def test_panel_view_with_invalid_selection1_status_code(self):
		url = '{0}{1}'.format(reverse('panel'), '?geloescht=99&userid_name__zi_organisation=ZZ-XX')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Keine Treffer")

	def test_panel_view_with_invalid_selection2_status_code(self):
		url = '{0}{1}'.format(reverse('panel'), '?DAS_FELD_GIBTS_NICHT=1')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "User_xv10099")

class Panel_exportCSVTest(TestCase):
	# User / Rolle / AF : Das wird mal die Hauptseite für
	# Aktualisierungen / Ergänzungen / Löschungen von Rollen und Verbindungen
	def setUp(self):
		Anmeldung(self.client.login)
		Setup_database()

		TblOrga.objects.create(
			team = 'Django-Team-01',
			themeneigentuemer = 'Ihmchen_01'
		)

		TblUebersichtAfGfs.objects.create(
			name_gf_neu =			'rvg_00458_neueGF mit echt mehr Zeichen als üblich',
			name_af_neu =			'rva_00458_neue_AF auch mit mehr Zeichen als üblich',
			kommentar =				'Kein Kommentar',
			zielperson =			'Lutz',
			af_text =				'Das ist der AF-normaltext',
			gf_text = 				'Das ist der GF-normaltext',
			af_langtext = 			'Das ist der AF-Laaaaaaaaaaaaaaaaaaaaaaaaaaaaaaang-Text',
			af_ausschlussgruppen =	'Das soll niemand außer mir bekommen!!!',
			af_einschlussgruppen =	'das soll die ganze Welt erhalten können',
			af_sonstige_vergabehinweise = 'Keine Hinweise',
			geloescht =				False,
			kannweg = 				False,
			modelliert = 			timezone.now(),
		)
		TblUebersichtAfGfs.objects.create(
			name_gf_neu =			'rvg_00500_neueAF mit echt mehr Zeichen als üblich',
			name_af_neu =			'rva_00500_neue_AF auch mit mehr Zeichen als üblich',
		)
		TblUebersichtAfGfs.objects.create(
			name_gf_neu =			'rvg_00380_neueAF mit echt mehr Zeichen als üblich',
			name_af_neu =			'rva_00380_neue_AF auch mit mehr Zeichen als üblich',
		)

		TblUserIDundName.objects.create(
			userid = 			'xv10099',
			name = 				'User_xv10099',
			orga = 				TblOrga.objects.get(team = 'Django-Team-01'),
			zi_organisation =	'AI-BA',
			geloescht = 		False,
			abteilung = 		'ZI-AI-BA',
			gruppe = 			'ZI-AI-BA-PS',
		)

		TblPlattform.objects.create(tf_technische_plattform = 'RACFP')

		TblGesamt.objects.create(
			userid_name = 			TblUserIDundName.objects.get(userid = 'xv10099'),
			tf = 					'Die superlange schnuckelige TF',
			tf_beschreibung = 		'Die superlange schnuckelige TF-Beschreibung',
			enthalten_in_af = 		'rva_00458_neue_AF auch mit mehr Zeichen als üblich',
			modell = 				TblUebersichtAfGfs.objects.get(name_af_neu='rva_00380_neue_AF auch mit mehr Zeichen als üblich',
																   name_gf_neu='rvg_00380_neueAF mit echt mehr Zeichen als üblich'),
			tf_kritikalitaet = 		'Superkritisch sich ist das auch schon zu lang',
			tf_eigentuemer_org = 	'Keine Ahnung Org',
			plattform = 			TblPlattform.objects.get(tf_technische_plattform = 'RACFP'),
			gf = 					'rvg_00380_neueGF mit echt mehr Zeichen als üblich',
			vip_kennzeichen = 		'',
			zufallsgenerator = 		'',
			af_gueltig_ab = 		timezone.now() - timedelta(days=365),
			af_gueltig_bis = 		timezone.now() + timedelta(days=365),
			direct_connect = 		'no direct connect',
			hoechste_kritikalitaet_tf_in_af = 'u',
			gf_beschreibung = 		'Die superlange, mindestens 250 Zeichen umfassende GF-Beschreibung. Hier könnte man auch mal nach CRLF suchen',
			af_zuweisungsdatum = 	timezone.now() - timedelta(days=200),
			datum = 				timezone.now() - timedelta(days=500),
			geloescht = 			False,
			gefunden = 				True,
			wiedergefunden = 		timezone.now(),
			geaendert = 			False,
			neueaf = 				'',
			nicht_ai = 				False,
			patchdatum = 			None,
			wertmodellvorpatch =	'Hier kommt nix rein',
			loeschdatum = 			None,
			letzte_aenderung =		None
		)

		TblGesamt.objects.create(
			userid_name = 			TblUserIDundName.objects.get(userid = 'xv10099'),
			tf = 					'Die superlange schnuckelige TF2',
			tf_beschreibung = 		'Die superlange schnuckelige TF-Beschreibung',
			enthalten_in_af = 		'rva_00458_neue_AF auch mit mehr Zeichen als üblich',
			modell = 				TblUebersichtAfGfs.objects.get(name_af_neu='rva_00458_neue_AF auch mit mehr Zeichen als üblich',
																   name_gf_neu='rvg_00458_neueGF mit echt mehr Zeichen als üblich'),
			tf_kritikalitaet = 		'Superkritisch sich ist das auch schon zu lang',
			tf_eigentuemer_org = 	'Keine Ahnung Org',
			plattform = 			TblPlattform.objects.get(tf_technische_plattform = 'RACFP'),
			gf = 					'rvg_00458_neueAF mit echt mehr Zeichen als üblich',
			vip_kennzeichen = 		'',
			zufallsgenerator = 		'',
			af_gueltig_ab = 		timezone.now() - timedelta(days=365),
			af_gueltig_bis = 		timezone.now() + timedelta(days=365),
			direct_connect = 		'no direct connect',
			hoechste_kritikalitaet_tf_in_af = 'u',
			gf_beschreibung = 		'Die superlange, mindestens 250 Zeichen umfassende GF-Beschreibung. Hier könnte man auch mal nach CRLF suchen',
			af_zuweisungsdatum = 	timezone.now() - timedelta(days=200),
			datum = 				timezone.now() - timedelta(days=500),
			geloescht = 			False,
			gefunden = 				True,
			wiedergefunden = 		timezone.now(),
			geaendert = 			False,
			neueaf = 				'',
			nicht_ai = 				False,
			patchdatum = 			None,
			wertmodellvorpatch =	'Hier kommt nix rein',
			loeschdatum = 			None,
			letzte_aenderung =		None
		)

	# Eine leere Auswahl
	def test_panel_online_without_selection(self):
		url = reverse('panel_download')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "tf;tf_beschreibung;enthalten_in_af;name;userid;team;name_af_neu;name_gf_neu", 1)
		self.assertContains(response, "Die superlange schnuckelige TF;Die superlange schnuckelige TF-Beschreibung;", 1)
		self.assertContains(response, "Die superlange schnuckelige TF2;Die superlange schnuckelige TF-Beschreibung;", 1)
		self.assertContains(response, "rva_00458_neue_AF auch mit mehr Zeichen als ", 3)
		self.assertContains(response, "rvg_00458_neueGF mit echt mehr Zeichen als ", 1)
		self.assertContains(response, "User_xv10099;xv10099;AI-BA;", 2)
		self.assertContains(response, "rva_00380_neue_AF auch mit mehr Zeichen als ", 1)
		self.assertContains(response, "rvg_00380_neueAF mit echt mehr Zeichen als ", 1)

	# Eine gültige Auswahl für einen User in einer Gruppe
	def test_panel_online_with_valid_selection(self):
		url = '{0}{1}'.format(reverse('panel_download'), '?tf=TF2')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "tf;tf_beschreibung;enthalten_in_af;name;userid;team;name_af_neu;name_gf_neu", 1)
		self.assertNotContains(response, "Die superlange schnuckelige TF;")
		self.assertNotContains(response, "rva_00380_neue_AF auch mit mehr Zeichen als ")
		self.assertNotContains(response, "rvg_00380_neueAF mit echt mehr Zeichen als ")
		self.assertContains(response, "rva_00458_neue_AF auch mit mehr Zeichen als ", 2)
		self.assertContains(response, "rvg_00458_neueGF mit echt mehr Zeichen als ", 1)
		self.assertContains(response, "Die superlange schnuckelige TF2;Die superlange schnuckelige TF-Beschreibung;", 1)
		self.assertContains(response, "User_xv10099;xv10099;AI-BA;", 1)


class User_rolle_afTests_generate_pdf(TestCase):
	# Der Testfall muss aufgrund der PDF-Lieferung separat gehalten werden
	def setUp(self):
		Anmeldung(self.client.login)
		Setup_database()
		TblOrga.objects.create (
			team = 'Django-Team-01',
			themeneigentuemer = 'Ihmchen_01',
		)

		TblAfliste.objects.create (
			af_name = 			'rva_01219_beta91_job_abst',
			neu_ab = 			timezone.now(),
		)

		TblAfliste.objects.create (
			af_name = 			'rva_01219_beta91_job_abst_nicht_zugewiesen',
			neu_ab = 			timezone.now(),
		)

		# Drei User: XV und DV aktiv, AV gelöscht
		TblUserIDundName.objects.create (
			userid = 			'xv13254',
			name = 				'User_xv13254',
			orga = 				TblOrga.objects.get(team = 'Django-Team-01'),
			zi_organisation =	'AI-BA',
			geloescht = 		False,
			abteilung = 		'ZI-AI-BA',
			gruppe = 			'ZI-AI-BA-PS',
		)
		TblUserIDundName.objects.create (
			userid = 			'dv13254',
			name = 				'User_xv13254',
			orga = 				TblOrga.objects.get(team = 'Django-Team-01'),
			zi_organisation =	'AI-BA',
			geloescht = 		False,
			abteilung = 		'ZI-AI-BA',
			gruppe = 			'ZI-AI-BA-PS',
		)
		TblUserIDundName.objects.create (
			userid = 			'av13254',
			name = 				'User_xv13254',
			orga = 				TblOrga.objects.get(team = 'Django-Team-01'),
			zi_organisation =	'AI-BA',
			geloescht = 		True,
			abteilung = 		'ZI-AI-BA',
			gruppe = 			'ZI-AI-BA-PS',
		)

		# Zwei Rollen, die auf den XV-User vergeben werden
		TblRollen.objects.create (
			rollenname = 		'Erste Neue Rolle',
			system =			'Testsystem',
			rollenbeschreibung = 'Das ist eine Testrolle',
		)
		TblRollen.objects.create (
			rollenname = 		'Zweite Neue Rolle',
			system =			'Irgendein System',
			rollenbeschreibung = 'Das ist auch eine Testrolle',
		)

		# Drei AF-Zuordnungen
		TblRollehataf.objects.create (
			mussfeld =			True,
			einsatz =			TblRollehataf.EINSATZ_XABCV,
			bemerkung = 		'Irgend eine halbwegs sinnvolle Beschreibung',
			af = 				TblAfliste.objects.get(af_name = 'rva_01219_beta91_job_abst'),
			rollenname = 		TblRollen.objects.get(rollenname= 'Erste Neue Rolle'),
		)
		TblRollehataf.objects.create (
			mussfeld =			True,
			einsatz =			TblRollehataf.EINSATZ_XABCV,
			bemerkung = 		'Irgend eine halbwegs sinnvolle Beschreibung',
			af = 				TblAfliste.objects.get(af_name = 'rva_01219_beta91_job_abst_nicht_zugewiesen'),
			rollenname = 		TblRollen.objects.get(rollenname= 'Erste Neue Rolle'),
		)
		TblRollehataf.objects.create (
			mussfeld =			False,
			einsatz =			TblRollehataf.EINSATZ_XABCV,
			bemerkung = 		'Auch irgend eine halbwegs sinnvolle Beschreibung',
			af = 				TblAfliste.objects.get(af_name = 'rva_01219_beta91_job_abst'),
			rollenname = 		TblRollen.objects.get(rollenname= 'Zweite Neue Rolle'),
		)

		# Dem XV-User werden zwei Rollen zugewiesen, dem AV- und DV-User keine
		TblUserhatrolle.objects.create(
			userid =	 		TblUserIDundName.objects.get(userid = 'xv13254'),
			rollenname = 		TblRollen.objects.first(),
			schwerpunkt_vertretung = 'Schwerpunkt',
			bemerkung = 		'Das ist eine Testrolle für ZI-AI-BA-PS',
			letzte_aenderung= 	timezone.now(),
		)
		TblUserhatrolle.objects.create(
			userid =	 		TblUserIDundName.objects.get(userid = 'xv13254'),
			rollenname = 		TblRollen.objects.get(rollenname = 'Zweite Neue Rolle'),
			schwerpunkt_vertretung = 'Vertretung',
			bemerkung = 		'Das ist auch eine Testrolle für ZI-AI-BA-PS',
			letzte_aenderung= 	timezone.now(),
		)

		# Die nächsten beiden Objekte werden für tblGesamt als ForeignKey benötigt
		TblUebersichtAfGfs.objects.create(
			name_gf_neu = 		"GF-foo in tblÜbersichtAFGF",
			name_af_neu =		"AF-foo in tblÜbersichtAFGF",
			zielperson = 		'Fester BesterTester'
		)
		TblUebersichtAfGfs.objects.create(
			name_gf_neu = 		"GF-foo-gelöscht in tblÜbersichtAFGF",
			name_af_neu =		"AF-foo-gelöscht in tblÜbersichtAFGF",
			zielperson = 		'Fester BesterTester'
		)
		TblPlattform.objects.create(
			tf_technische_plattform = 'Test-Plattform'
		)

		# Getestet werden soll die Möglichkeit,
		# für einen bestimmten User festzustellen, ob er über eine definierte AF verfügt
		# und diese auch auf aktiv gesetzt ist
		TblGesamt.objects.create(
			userid_name = 		TblUserIDundName.objects.get(userid = 'xv13254'),
			tf = 				'foo-TF',
			tf_beschreibung = 	'TF-Beschreibung für foo-TF',
			enthalten_in_af = 	'Sollte die AF rva_01219_beta91_job_abst sein',
			modell =			TblUebersichtAfGfs.objects.get(name_gf_neu = "GF-foo in tblÜbersichtAFGF"),
			plattform = 		TblPlattform.objects.get(tf_technische_plattform = 'Test-Plattform'),
			gf = 				'GF-foo',
			datum = 			timezone.now(),
			geloescht = 		False,
		)

		# und hier noch ein bereits gelöschtes Recht auf TF-Ebene.
		# ToDo Noch eine komplette AF mit allen GFs als gelöscht markiert vorbereiten
		TblGesamt.objects.create(
			userid_name = 		TblUserIDundName.objects.get(userid = 'xv13254'),
			tf = 				'foo-TF-gelöscht',
			tf_beschreibung = 	'TF-Beschreibung für foo-TF-gelöscht',
			enthalten_in_af = 	'Sollte die AF rva_01219_beta91_job_abst sein',
			modell =			TblUebersichtAfGfs.objects.get(name_gf_neu = "GF-foo in tblÜbersichtAFGF"),
			plattform = 		TblPlattform.objects.get(tf_technische_plattform = 'Test-Plattform'),
			gf = 				'GF-foo',
			datum = 			timezone.now() - timedelta(days=365),
			geloescht = 		True,
		)
	def test_panel_view_use_konzept_pdf(self):
		pdf_url = reverse('uhr_konzept_pdf')
		response = self.client.get(pdf_url)
		self.assertEqual(response.status_code, 200)

class User_rolle_afTests(TestCase):
	# User / Rolle / AF: Die Hauptseite für Aktualisierungen / Ergänzungen / Löschungen von Rollen und Verbindungen
	def setUp(self):
		Anmeldung(self.client.login)
		Setup_database()
		TblOrga.objects.create (
			team = 'Django-Team-01',
			themeneigentuemer = 'Ihmchen_01',
		)

		TblOrga.objects.create (
			team = 'Django-Team-02',
			themeneigentuemer = 'Ihmchen_02',
		)

		TblAfliste.objects.create (
			af_name = 			'rva_01219_beta91_job_abst',
			neu_ab = 			timezone.now(),
		)

		TblAfliste.objects.create (
			af_name = 			'rva_01219_beta91_job_abst_nicht_zugewiesen',
			neu_ab = 			timezone.now(),
		)

		# Drei User: XV und DV aktiv, AV gelöscht
		TblUserIDundName.objects.create (
			userid = 			'xv13254',
			name = 				'User_xv13254',
			orga = 				TblOrga.objects.get(team = 'Django-Team-01'),
			zi_organisation =	'AI-BA',
			geloescht = 		False,
			abteilung = 		'ZI-AI-BA',
			gruppe = 			'ZI-AI-BA-PS',
		)
		TblUserIDundName.objects.create (
			userid = 			'dv13254',
			name = 				'User_xv13254',
			orga = 				TblOrga.objects.get(team = 'Django-Team-01'),
			zi_organisation =	'AI-BA',
			geloescht = 		False,
			abteilung = 		'ZI-AI-BA',
			gruppe = 			'ZI-AI-BA-PS',
		)
		TblUserIDundName.objects.create (
			userid = 			'av13254',
			name = 				'User_xv13254',
			orga = 				TblOrga.objects.get(team = 'Django-Team-01'),
			zi_organisation =	'AI-BA',
			geloescht = 		True,
			abteilung = 		'ZI-AI-BA',
			gruppe = 			'ZI-AI-BA-PS',
		)

		# Zwei Rollen, die auf den XV-User vergeben werden
		TblRollen.objects.create (
			rollenname = 		'Erste Neue Rolle',
			system =			'Testsystem',
			rollenbeschreibung = 'Das ist eine Testrolle',
		)
		TblRollen.objects.create (
			rollenname = 		'Zweite Neue Rolle',
			system =			'Irgendein System',
			rollenbeschreibung = 'Das ist auch eine Testrolle',
		)

		# Drei AF-Zuordnungen
		TblRollehataf.objects.create (
			mussfeld =			True,
			einsatz =			TblRollehataf.EINSATZ_XABCV,
			bemerkung = 		'Irgend eine halbwegs sinnvolle Beschreibung',
			af = 				TblAfliste.objects.get(af_name = 'rva_01219_beta91_job_abst'),
			rollenname = 		TblRollen.objects.get(rollenname= 'Erste Neue Rolle'),
		)
		TblRollehataf.objects.create (
			mussfeld =			True,
			einsatz =			TblRollehataf.EINSATZ_XABCV,
			bemerkung = 		'Irgend eine halbwegs sinnvolle Beschreibung',
			af = 				TblAfliste.objects.get(af_name = 'rva_01219_beta91_job_abst_nicht_zugewiesen'),
			rollenname = 		TblRollen.objects.get(rollenname= 'Erste Neue Rolle'),
		)
		TblRollehataf.objects.create (
			mussfeld =			False,
			einsatz =			TblRollehataf.EINSATZ_XABCV,
			bemerkung = 		'Auch irgend eine halbwegs sinnvolle Beschreibung',
			af = 				TblAfliste.objects.get(af_name = 'rva_01219_beta91_job_abst'),
			rollenname = 		TblRollen.objects.get(rollenname= 'Zweite Neue Rolle'),
		)

		# Dem XV-User werden zwei Rollen zugewiesen, dem AV- und DV-User keine
		TblUserhatrolle.objects.create(
			userid =	 		TblUserIDundName.objects.get(userid = 'xv13254'),
			rollenname = 		TblRollen.objects.first(),
			schwerpunkt_vertretung = 'Schwerpunkt',
			bemerkung = 		'Das ist eine Testrolle für ZI-AI-BA-PS',
			letzte_aenderung= 	timezone.now(),
		)
		TblUserhatrolle.objects.create(
			userid =	 		TblUserIDundName.objects.get(userid = 'xv13254'),
			rollenname = 		TblRollen.objects.get(rollenname = 'Zweite Neue Rolle'),
			schwerpunkt_vertretung = 'Vertretung',
			bemerkung = 		'Das ist auch eine Testrolle für ZI-AI-BA-PS',
			letzte_aenderung= 	timezone.now(),
		)

		# Die nächsten beiden Objekte werden für tblGesamt als ForeignKey benötigt
		TblUebersichtAfGfs.objects.create(
			name_gf_neu = 		"GF-foo in tblÜbersichtAFGF",
			name_af_neu =		"AF-foo in tblÜbersichtAFGF",
			zielperson = 		'Fester BesterTester'
		)
		TblUebersichtAfGfs.objects.create(
			name_gf_neu = 		"GF-foo-gelöscht in tblÜbersichtAFGF",
			name_af_neu =		"AF-foo-gelöscht in tblÜbersichtAFGF",
			zielperson = 		'Fester BesterTester'
		)
		TblPlattform.objects.create(
			tf_technische_plattform = 'Test-Plattform'
		)

		# Getestet werden soll die Möglichkeit,
		# für einen bestimmten User festzustellen, ob er über eine definierte AF verfügt
		# und diese auch auf aktiv gesetzt ist
		TblGesamt.objects.create(
			userid_name = 		TblUserIDundName.objects.get(userid = 'xv13254'),
			tf = 				'foo-TF',
			tf_beschreibung = 	'TF-Beschreibung für foo-TF',
			enthalten_in_af = 	'Sollte die AF rva_01219_beta91_job_abst sein',
			modell =			TblUebersichtAfGfs.objects.get(name_gf_neu = "GF-foo in tblÜbersichtAFGF"),
			plattform = 		TblPlattform.objects.get(tf_technische_plattform = 'Test-Plattform'),
			gf = 				'GF-foo',
			datum = 			timezone.now(),
			geloescht = 		False,
		)

		# und hier noch ein bereits gelöschtes Recht auf TF-Ebene.
		# ToDo Noch eine komplette AF mit allen GFs als gelöscht markiert vorbereiten
		TblGesamt.objects.create(
			userid_name = 		TblUserIDundName.objects.get(userid = 'xv13254'),
			tf = 				'foo-TF-gelöscht',
			tf_beschreibung = 	'TF-Beschreibung für foo-TF-gelöscht',
			enthalten_in_af = 	'Sollte die AF rva_01219_beta91_job_abst sein',
			modell =			TblUebersichtAfGfs.objects.get(name_gf_neu = "GF-foo in tblÜbersichtAFGF"),
			plattform = 		TblPlattform.objects.get(tf_technische_plattform = 'Test-Plattform'),
			gf = 				'GF-foo',
			datum = 			timezone.now() - timedelta(days=365),
			geloescht = 		True,
		)


	# Ist die Seite da?
	def test_panel_view_status_code(self):
		url = reverse('user_rolle_af')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
	def test_panel_view_with_valid_selection_status_code(self):
		url = '{0}{1}'.format(reverse('user_rolle_af'), '?name=UseR&gruppe=BA-ps')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "xv13254")
	# Hat der User zwei Rollen (XV un DV)?
	def test_panel_view_num_userids(self):
		id = TblUserIDundName.objects.get(userid='xv13254').id
		url = '{0}{1}/{2}'.format(reverse('user_rolle_af'), id, '?name=UseR&gruppe=BA-ps')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "xv13254")
		self.assertContains(response, "dv13254")
	def test_panel_view_num_roles(self):
		id = TblUserIDundName.objects.get(userid='xv13254').id
		url = '{0}{1}/{2}'.format(reverse('user_rolle_af'), id, '?name=UseR&gruppe=BA-ps')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "User_xv13254")
		#print('_____________')
		#print (response.content)
		self.assertContains(response, '(2 Rollen,')
	# Sind bei einer der Rollen ein Recht nicht vergeben und zwei Rechte vergeben und insgesamt 3 Rechte behandelt?
	def test_panel_view_with_deep_insight(self):
		id = TblUserIDundName.objects.get(userid='xv13254').id
		url = '{0}{1}/{2}'.format(reverse('user_rolle_af'), id, '?name=UseR&gruppe=BA-ps')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "User_xv13254")
		self.assertContains(response, 'icon-yes', 4)
		self.assertContains(response, 'icon-no', 2)
	def test_panel_view_with_deep_insight_find_delete_link(self):
		id = TblUserIDundName.objects.get(userid='xv13254').id
		url = '{0}{1}/{2}'.format(reverse('user_rolle_af'), id, '?name=UseR&gruppe=BA-ps')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "User_xv13254")
		rolle1 = TblUserhatrolle.objects.get(userid = 'xv13254', rollenname = 'Erste Neue Rolle')
		rolle2 = TblUserhatrolle.objects.get(userid = 'xv13254', rollenname = 'Zweite Neue Rolle')
		self.assertContains(response, '/rapp/user_rolle_af/{}/delete/?'.format(rolle1), 1)
		self.assertContains(response, '/rapp/user_rolle_af/{}/delete/?'.format(rolle2), 1)

		# Zum Abschluss klicken wir mal auf die Löschlinks und erhalten die Sicherheitsabfrage.
		# Erster Link
		loeschurl = '/rapp/user_rolle_af/{}/delete/'.format(rolle1)
		response = self.client.get(loeschurl)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, '<p>Sie löschen gerade den folgenden Rollen-Eintrag:</p>')
		self.assertContains(response, '<p>"Erste Neue Rolle":</p>')
		# Zweiter Link
		loeschurl = '/rapp/user_rolle_af/{}/delete/'.format(rolle2)
		response = self.client.get(loeschurl)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, '<p>Sie löschen gerade den folgenden Rollen-Eintrag:</p>')
		self.assertContains(response, '<p>"Zweite Neue Rolle":</p>')

	def test_panel_view_with_deep_insight_find_change_link(self):
		id = TblUserIDundName.objects.get(userid='xv13254').id
		url = '{0}{1}/{2}'.format(reverse('user_rolle_af'), id, '?name=UseR&gruppe=BA-ps')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "User_xv13254")

		rolle1 = TblUserhatrolle.objects.get(userid = 'xv13254', rollenname = 'Erste Neue Rolle')
		rolle2 = TblUserhatrolle.objects.get(userid = 'xv13254', rollenname = 'Zweite Neue Rolle')
		changeurl1 = '/adminrapp/tbluserhatrolle/{}/change/?'.format(rolle1)
		changeurl2 = '/adminrapp/tbluserhatrolle/{}/change/?'.format(rolle2)

		self.assertContains(response, changeurl1, 1)
		self.assertContains(response, changeurl2, 1)

		# ToDo Zum Abschluss klicken wir mal auf die Change-Links und erhalten den Änderungsdialog.
		"""
		Aus welchen Gründen auch immer das hier nur zu einer Weiterleitung 302 führt...
		# Erster Link
		response = self.client.get(changeurl1)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'User und Ihre Rollen ändern')
		self.assertContains(response, '<option value="Erste Neue Rolle">')
		#Zweiter Link
		response = self.client.get(changeurl2)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'User und Ihre Rollen ändern')
		self.assertContains(response, '<option value="Zweite Neue Rolle">')
		"""
	def test_panel_view_with_deep_insight_find_create_link(self):
		id = TblUserIDundName.objects.get(userid='xv13254').id
		url = '{0}{1}/{2}'.format(reverse('user_rolle_af'), id, '?name=UseR&gruppe=BA-ps')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "User_xv13254")
		self.assertContains(response, '/rapp/user_rolle_af/create/xv13254/?&', 1)

		# Zum Abschluss klicken wir mal auf den Create-Link und erhalten den Erstellungsdialog.
		createurl = '/rapp/user_rolle_af/create/xv13254/?&name=&orga=1&rollenname=&gruppe=&user='
		response = self.client.get(createurl)
		self.assertEqual(response.status_code, 200)
		# print('____________')
		# print(response.content)
		self.assertContains(response, 'Rollen-Eintrag ergänzen für')
		self.assertContains(response, '<option value="xv13254">xv13254 | User_xv13254</option>')
		self.assertContains(response, '<option value="" selected>---------</option>', 2)
		self.assertContains(response, '<option value="">---------</option>', 1)

	def test_panel_view_with_invalid_selection_status_code(self):
		url = '{0}{1}'.format(reverse('user_rolle_af'), '?geloescht=99&zi_organisation=ZZ-XX')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Keine angezeigten User")
	def test_panel_view_with_invalid_selection_returns_complete_list_status_code(self):
		url = '{0}{1}'.format(reverse('user_rolle_af'), '?DAS_FELD_GIBTS_NICHT=1')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "User_xv13254")
	def test_panel_view_contains_link_back_to_home_view(self):
		new_user_url = reverse('user_rolle_af')
		userlist_url = reverse('home')
		response = self.client.get(new_user_url)
		self.assertContains(response, 'href="{0}"'.format(userlist_url))
	# Gibt es den "Konzept" Button?
	def test_panel_view_contains_link_to_konzept_view(self):
		url = reverse('user_rolle_af')
		konzept_url = reverse('uhr_konzept')
		response = self.client.get(url)
		self.assertContains(response, 'href="{0}?"'.format(konzept_url))
	def test_panel_view_contains_link_to_matrix_view(self):
		url = reverse('user_rolle_af')
		konzept_url = reverse('uhr_matrix')
		response = self.client.get(url)
		self.assertContains(response, 'href="{0}?"'.format(konzept_url))
	def test_panel_view_contains_no_user_first(self):
		url = reverse('user_rolle_af')
		response = self.client.get(url)
		self.assertContains(response, 'Kein User selektiert', 1)
	def test_panel_view_use_konzept_view(self):
		url = reverse('uhr_konzept')
		pdf_url = reverse('uhr_konzept_pdf')
		response = self.client.get(url)
		self.assertContains(response, 'href="{0}?"'.format(pdf_url))
		self.assertContains(response, 'Erste Neue Rolle', 1)
		self.assertContains(response, 'Zweite Neue Rolle', 1)
		self.assertContains(response, 'rva_01219_beta91_job_abst', 3)
		self.assertContains(response, 'Das ist eine Testrolle', 1)
		self.assertContains(response, 'Das ist auch eine Testrolle', 1)
		self.assertContains(response, 'Testsystem', 1)
		self.assertContains(response, 'Irgendein System', 1)
	def test_panel_view_use_matrix_view(self):
		url = reverse('uhr_matrix')
		pdf_url = reverse('uhr_matrix_csv')
		response = self.client.get(url)
		self.assertContains(response, 'href="{0}?"'.format(pdf_url))
		self.assertContains(response, '<small>Erste Neue Rolle</small>', 1)
		self.assertContains(response, '<small>Zweite Neue Rolle</small>', 1)
		self.assertContains(response, 'User_xv13254', 2)
		self.assertContains(response, 'Schwerpunkt', 1)
		self.assertContains(response, 'Vertretung', 1)

	# Suche nach dem User und ob seiner UserID mindestens eine Rolle zugeodnet ist.
	# Falls ja, suche weiter nach der Liste der AFen zu der Rolle (Auszug).
	# Im Detail: Wir suchen über /.../user_rolle_af/<Nummer des Eintrags UserHatRolle>
	# nach dem konkreten Eintrag (die Nummer variiert über die Anzahl der ausgeführten Testfälle,
	# deshalb das etwas umständliche Gesuche unten).
	def test_panel_view_with_valid_selection_find_UserHatRolle_id(self):
		url = '{0}{1}'.format(reverse('user_rolle_af'), '?name=&orga=1&gruppe=&pagesize=100')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "User_xv13254")  # Die UserID gibt es schon mal

		suchstr = "Wir haben in der ReST-Schreibweise keinen Treffer gelandet!"
		for k in response:
			foo = re.search('/user_rolle_af/(\d+)/', str(k))
			if foo != None:
				suchstr = re.split('/', str(foo))
				suchstr = ("/{}/{}/".format(suchstr[1], suchstr[2]))
		self.assertContains(response, suchstr)  # Die UserIDhatRolle-Zeile wurde in der ReST-Schreibweise gefunden

	def test_panel_view_with_valid_selection_find_accordeon_link(self):
		url = '{0}{1}'.format(reverse('user_rolle_af'), '?name=&orga=1&gruppe=&pagesize=100')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)

		for k in response:
			foo = re.search('/user_rolle_af/(\d+)/', str(k))
			if foo != None:
				suchstr = re.split('/', str(foo))
				url = '{0}{1}/{2}'.format(reverse('user_rolle_af'),
										   suchstr[2],
										   '?name=&orga=1&gruppe=&pagesize=100')
				# print ()
				# print ('suche nach folgender URL: {}'.format (url))
				response = self.client.get(url)
				self.assertEqual(response.status_code, 200)
			else:
				self.assertFalse(True)	# Das war nix - offensichtlich die URL nicht korrekt
		self.assertContains(response, 'Erste Neue Rolle') # Rollenname
		self.assertContains(response, 'Testsystem') # System
		self.assertContains(response, 'Das ist eine Testrolle') # Beschreibung in TblRollen
		self.assertContains(response, 'rva_01219_beta91_job_abst') # Die gesuchte AF eine Stufe tiefer
		self.assertContains(response, 'Das ist eine Testrolle für ZI-AI-BA-PS') # Beschreibung in TblUserHatRolle
		self.assertContains(response, 'Schwerpunkt') # Wertigkeit in der Verantwortungsmatrix

class User_rolle_variantsTest(TestCase):
	# User / Rolle / AF : Das wird mal die Hauptseite für
	# Aktualisierungen / Ergänzungen / Löschungen von Rollen und Verbindungen
	def setUp(self):
		Anmeldung(self.client.login)
		Setup_database()
		TblOrga.objects.create (
			team = 'Django-Team-01',
			themeneigentuemer = 'Ihmchen_01',
		)

		TblOrga.objects.create (
			team = 'Django-Team-02',
			themeneigentuemer = 'Ihmchen_02',
		)

		TblAfliste.objects.create (
			af_name = 			'rva_01219_beta91_job_abst',
			neu_ab = 			timezone.now(),
		)

		TblAfliste.objects.create (
			af_name = 			'rva_01219_beta91_job_abst_nicht_zugewiesen',
			neu_ab = 			timezone.now(),
		)

		# Drei UserIDen für eine Identität: XV und DV aktiv, AV gelöscht
		TblUserIDundName.objects.create (
			userid = 			'xv13254',
			name = 				'User_xv13254',
			orga = 				TblOrga.objects.get(team = 'Django-Team-01'),
			zi_organisation =	'AI-BA',
			geloescht = 		False,
			abteilung = 		'ZI-AI-BA',
			gruppe = 			'ZI-AI-BA-LS',
		)
		TblUserIDundName.objects.create (
			userid = 			'dv13254',
			name = 				'User_xv13254',
			orga = 				TblOrga.objects.get(team = 'Django-Team-01'),
			zi_organisation =	'AI-BA',
			geloescht = 		False,
			abteilung = 		'ZI-AI-BA',
			gruppe = 			'ZI-AI-BA-LS',
		)
		TblUserIDundName.objects.create (
			userid = 			'av13254',
			name = 				'User_xv13254',
			orga = 				TblOrga.objects.get(team = 'Django-Team-01'),
			zi_organisation =	'AI-BA',
			geloescht = 		True,
			abteilung = 		'ZI-AI-BA',
			gruppe = 			'ZI-AI-BA-LS',
		)

		# Eine UserID für eine weitere Identität: XV aktiv
		TblUserIDundName.objects.create (
			userid = 			'xv00042',
			name = 				'User_xv00042',
			orga = 				TblOrga.objects.get(team = 'Django-Team-01'),
			zi_organisation =	'AI-BA',
			geloescht = 		False,
			abteilung = 		'ZI-AI-BA',
			gruppe = 			'ZI-AI-BA-LS',
		)

		# Eine UserID für eine weitere Identität: XV aktiv: Für diesen User gibt es noch keine eingetragene Rolle
		TblUserIDundName.objects.create (
			userid = 			'xv00023',
			name = 				'User_xv00023',
			orga = 				TblOrga.objects.get(team = 'Django-Team-01'),
			zi_organisation =	'AI-BA',
			geloescht = 		False,
			abteilung = 		'ZI-AI-BA',
			gruppe = 			'ZI-AI-BA-LS',
		)

		# Zwei Rollen, die auf den ersten XV-User vergeben werden, die zweite wird auch dem m2. User vergeben
		TblRollen.objects.create (
			rollenname = 		'Erste Neue Rolle',
			system =			'Testsystem',
			rollenbeschreibung = 'Das ist eine Testrolle',
		)
		TblRollen.objects.create (
			rollenname = 		'Zweite Neue Rolle',
			system =			'Irgendein System',
			rollenbeschreibung = 'Das ist auch eine Testrolle',
		)

		# Drei AF-Zuordnungen zu Rollen
		TblRollehataf.objects.create (
			mussfeld =			True,
			einsatz =			TblRollehataf.EINSATZ_XABCV,
			bemerkung = 		'Irgend eine halbwegs sinnvolle Beschreibung',
			af = 				TblAfliste.objects.get(af_name = 'rva_01219_beta91_job_abst'),
			rollenname = 		TblRollen.objects.get(rollenname= 'Erste Neue Rolle'),
		)
		TblRollehataf.objects.create (
			mussfeld =			True,
			einsatz =			TblRollehataf.EINSATZ_XABCV,
			bemerkung = 		'Irgend eine halbwegs sinnvolle Beschreibung',
			af = 				TblAfliste.objects.get(af_name = 'rva_01219_beta91_job_abst_nicht_zugewiesen'),
			rollenname = 		TblRollen.objects.get(rollenname= 'Erste Neue Rolle'),
		)
		TblRollehataf.objects.create (
			mussfeld =			False,
			einsatz =			TblRollehataf.EINSATZ_XABCV,
			bemerkung = 		'Auch irgend eine halbwegs sinnvolle Beschreibung',
			af = 				TblAfliste.objects.get(af_name = 'rva_01219_beta91_job_abst'),
			rollenname = 		TblRollen.objects.get(rollenname= 'Zweite Neue Rolle'),
		)

		# User 12354_ Dem XV-User werden zwei Rollen zugewiesen, dem AV- und DV-User keine
		TblUserhatrolle.objects.create(
			userid =	 		TblUserIDundName.objects.get(userid = 'xv13254'),
			rollenname = 		TblRollen.objects.first(),
			schwerpunkt_vertretung = 'Schwerpunkt',
			bemerkung = 		'Das ist eine Testrolle für ZI-AI-BA-LS',
			letzte_aenderung= 	timezone.now(),
		)
		TblUserhatrolle.objects.create(
			userid =	 		TblUserIDundName.objects.get(userid = 'xv13254'),
			rollenname = 		TblRollen.objects.get(rollenname = 'Zweite Neue Rolle'),
			schwerpunkt_vertretung = 'Vertretung',
			bemerkung = 		'Das ist auch eine Testrolle für ZI-AI-BA-LS',
			letzte_aenderung= 	timezone.now(),
		)
		# Dem zweiten User 00042 wird nur eine Rolle zugeordnet
		TblUserhatrolle.objects.create(
			userid =	 		TblUserIDundName.objects.get(userid = 'xv00042'),
			rollenname = 		TblRollen.objects.first(),
			schwerpunkt_vertretung = 'Schwerpunkt',
			bemerkung = 		'Das ist eine Testrolle für ZI-AI-BA-LS',
			letzte_aenderung= 	timezone.now(),
		)
		# Und dem dritten User 00023 keine Rolle

		# Die nächsten beiden Objekte werden für tblGesamt als ForeignKey benötigt
		TblUebersichtAfGfs.objects.create(
			name_gf_neu = 		"GF-foo in tblÜbersichtAFGF",
			name_af_neu =		"AF-foo in tblÜbersichtAFGF",
			zielperson = 		'Fester BesterTester'
		)
		TblUebersichtAfGfs.objects.create(
			name_gf_neu = 		"GF-foo-gelöscht in tblÜbersichtAFGF",
			name_af_neu =		"AF-foo-gelöscht in tblÜbersichtAFGF",
			zielperson = 		'Fester BesterTester'
		)
		TblPlattform.objects.create(
			tf_technische_plattform = 'Test-Plattform'
		)

		# Getestet werden soll die Möglichkeit,
		# für einen bestimmten User festzustellen, ob er über eine definierte AF verfügt
		# und diese auch auf aktiv gesetzt ist
		TblGesamt.objects.create(
			userid_name = 		TblUserIDundName.objects.get(userid = 'xv13254'),
			tf = 				'foo-TF',
			tf_beschreibung = 	'TF-Beschreibung für foo-TF',
			enthalten_in_af = 	'rva_01219_beta91_job_abst',
			modell =			TblUebersichtAfGfs.objects.get(name_gf_neu = "GF-foo in tblÜbersichtAFGF"),
			plattform = 		TblPlattform.objects.get(tf_technische_plattform = 'Test-Plattform'),
			gf = 				'GF-foo',
			datum = 			timezone.now(),
			geloescht = 		False,
		)
		TblGesamt.objects.create(
			userid_name = 		TblUserIDundName.objects.get(userid = 'xv00042'),
			tf = 				'foo-TF',
			tf_beschreibung = 	'TF-Beschreibung für foo-TF',
			enthalten_in_af = 	'rva_01219_beta91_job_abst',
			modell =			TblUebersichtAfGfs.objects.get(name_gf_neu = "GF-foo in tblÜbersichtAFGF"),
			plattform = 		TblPlattform.objects.get(tf_technische_plattform = 'Test-Plattform'),
			gf = 				'GF-foo',
			datum = 			timezone.now(),
			geloescht = 		False,
		)

		# und hier noch ein bereits gelöschtes Recht auf TF-Ebene.
		# ToDo Noch eine komplette AF mit allen GFs als gelöscht markiert vorbereiten
		# ToDo Noch eine komplette AF mit GF und TFD in anderer Rolle vorbereiten
		TblGesamt.objects.create(
			userid_name = 		TblUserIDundName.objects.get(userid = 'xv13254'),
			tf = 				'foo-TF-gelöscht',
			tf_beschreibung = 	'TF-Beschreibung für foo-TF-gelöscht',
			enthalten_in_af = 	'rva_01219_beta91_job_abst',
			modell =			TblUebersichtAfGfs.objects.get(name_gf_neu = "GF-foo in tblÜbersichtAFGF"),
			plattform = 		TblPlattform.objects.get(tf_technische_plattform = 'Test-Plattform'),
			gf = 				'GF-foo',
			datum = 			timezone.now() - timedelta(days=365),
			geloescht = 		True,
		)

	# Ist die Seite da?
	def test_panel_01_view_status_code(self):
		url = reverse('user_rolle_af')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
	# Eine gültige Auswahl für einen User in einer Gruppe: Das nutzt noch das erste Panel in der Ergebnisanzeige
	def test_panel_02_view_with_valid_selection(self):
		url = '{0}{1}'.format(reverse('user_rolle_af'), '?name=UseR&gruppe=BA-ls')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "xv13254")
		self.assertNotContains(response, "Betrachtung von Rollenvarianten")
	def test_panel_03_view_with_valid_role_star_name_and_group(self):
		url = '{0}{1}'.format(reverse('user_rolle_af'), '?rollenname=*&name=UseR&gruppe=BA-ls')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "xv13254", 4)
		self.assertContains(response, "xv00042", 5)
		self.assertContains(response, "xv00023", 2)

	def test_panel_03a_view_with_valid_role_star_unique_name_and_group(self):
		url = '{0}{1}'.format(reverse('user_rolle_af'), '?rollenname=*&name=UseR_xv00023&gruppe=BA-ls')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertNotContains(response, "xv13254")
		self.assertNotContains(response, "xv00042")
		self.assertContains(response, "xv00023", 5)

	def test_panel_04_view_with_valid_role_star(self):
		url = '{0}{1}'.format(reverse('user_rolle_af'), '?rollenname=*')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "xv13254")
		self.assertContains(response, "Betrachtung von Rollenvarianten")
		self.assertContains(response, "rva_01219_beta91_job_abst", 5)
		# Beide Identitäten haben eine Rolle, für die es mehrere Varianten gibt.
		# ToDo Der Testfall muss angepasst werden, wenn die Doppelnennung von Rollen behandelt wird
		"""
		self.assertContains(response,
							'<a href="/rapp/user_rolle_af/xv00042/create/Erste%20Neue%20Rolle/Schwerpunkt?&rollenname=*#xv00042.rva_01219_beta91_job_abst">Erste Neue Rolle</a')
		self.assertContains(response,
							'<a href="/rapp/user_rolle_af/xv00042/create/Zweite%20Neue%20Rolle/Schwerpunkt?&rollenname=*#xv00042.rva_01219_beta91_job_abst">Zweite Neue Rolle</a>')
		self.assertContains(response,
							'<a href="/rapp/user_rolle_af/xv13254/create/Erste%20Neue%20Rolle/Schwerpunkt?&rollenname=*#xv13254.rva_01219_beta91_job_abst">Erste Neue Rolle</a>')
		self.assertContains(response,
							'<a href="/rapp/user_rolle_af/xv13254/create/Zweite%20Neue%20Rolle/Schwerpunkt?&rollenname=*#xv13254.rva_01219_beta91_job_abst">Zweite Neue Rolle</a>')
		"""
		# Die Löschlinks enthalten die Nummern der User-hat-Rolle-Definition. Das brauchen wir später nochmal
		erste_rolle_des_ersten_users = TblUserhatrolle.objects.get(userid=TblUserIDundName.objects.get(userid='xv13254'),
			rollenname=TblRollen.objects.first())
		zweite_rolle_des_ersten_users = TblUserhatrolle.objects.get(userid=TblUserIDundName.objects.get(userid='xv13254'),
			rollenname=TblRollen.objects.get(rollenname='Zweite Neue Rolle'))
		rolle_des_zweiten_users = TblUserhatrolle.objects.get(userid=TblUserIDundName.objects.get(userid='xv00042'),
															  rollenname=TblRollen.objects.first())
		str11 = '<a href="/rapp/user_rolle_af/{}/delete/?&rollenname=*&user=">'.format(erste_rolle_des_ersten_users)
		str12 = '<a href="/rapp/user_rolle_af/{}/delete/?&rollenname=*&user=">'.format(zweite_rolle_des_ersten_users)
		str2 = '<a href="/rapp/user_rolle_af/{}/delete/?&rollenname=*&user=">'.format(rolle_des_zweiten_users)

		self.assertContains(response, str11)
		self.assertContains(response, str12)
		self.assertContains(response, str2)

		# Zum Abschluss klicken wir mal auf einen der Löschlinks und erhalten die Sicherheitsabfrage:
		loeschurl = '/rapp/user_rolle_af/{}/delete/?&rollenname=*&user='.format(erste_rolle_des_ersten_users)
		response = self.client.get(loeschurl)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, '<p>Sie löschen gerade den folgenden Rollen-Eintrag:</p>')
		self.assertContains(response, '<p>"Erste Neue Rolle":</p>')

		response = self.client.post(loeschurl, {'rollenname': erste_rolle_des_ersten_users,
												'userid': TblUserIDundName.objects.get(userid='xv13254')
												})
		self.assertEqual(response.status_code, 302)
		# ToDo Hier sollte eigentlich ein Eintrag gelöscht worden sein - das klappt aber nicht (XSRF-Token?)
	def test_panel_06_view_with_valid_role_star(self):
		url = '{0}{1}'.format(reverse('user_rolle_af'), '?rollenname=*')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "xv13254")
		self.assertContains(response, "Betrachtung von Rollenvarianten")
		self.assertContains(response, "rva_01219_beta91_job_abst", 5)
		# Beide Identitäten haben eine Rolle, für die es mehrere Varianten gibt.
		# ToDo Der Testfall muss angepasst werden, wenn die Doppelnennung von Rollen behandelt wird
		"""
		for uid in ('xv13254', 'xv00042'):
			for xte in ('Erste', 'Zweite'):
				bastelstring = '<a href="/rapp/user_rolle_af/{}/create/{}%20Neue%20Rolle/Schwerpunkt?&rollenname=*#{}.rva_01219_beta91_job_abst">{} Neue Rolle</a>'\
							 .format (uid, xte, uid, xte)
				self.assertContains(response, bastelstring)
		"""
		# Zum Abschluss klicken wir mal auf einen der Löschlinks und erhalten die Sicherheitsabfrage:
		createurl = '/rapp/user_rolle_af/{}/create/{}%20Neue%20Rolle/Schwerpunkt?&rollenname=*#{}.rva_01219_beta91_job_abst' \
						   .format('xv00042', 'Zweite', 'xv00042')
		response = self.client.get(createurl)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Rollen-Eintrag ergänzen für <strong></strong>')
		self.assertContains(response, '<option value="">---------</option>', 3)
		self.assertContains(response, '<option value="xv00042">xv00042 | User_xv00042</option>')
		self.assertContains(response, '<option value="xv13254">xv13254 | User_xv13254</option>')
		self.assertContains(response, '<option value="dv13254">dv13254 | User_xv13254</option>')
		# ToDo Achtung, hier werden in der Liste auch gelöschte User angezeigt!
		# self.assertNotContains(response, '<option value="av13254">av13254 | User_xv13254</option>')
		self.assertContains(response, '<option value="Erste Neue Rolle">Erste Neue Rolle</option>')
		self.assertContains(response, '<option value="Zweite Neue Rolle" selected>Zweite Neue Rolle</option>')
		self.assertContains(response, '<option value="Schwerpunkt" selected>Schwerpunktaufgabe</option>')
		self.assertContains(response, '<option value="Vertretung">Vertretungstätigkeiten, Zweitsysteme</option>')
		self.assertContains(response, '<option value="Allgemein">Rollen, die nicht Systemen zugeordnet sind</option>')
		self.assertContains(response, '<th><label for="id_bemerkung">Bemerkung:</label></th><td><textarea name="bemerkung" cols="40" rows="10" id="id_bemerkung">')
		response = self.client.post(createurl, {'rollenname': "Erste Neue Rolle",
												'userid': TblUserIDundName.objects.get(userid='xv13254')
												})
		# Todo: Warum geht das? Die Rolle ist doch schon vergeben...
		self.assertEqual(response.status_code, 200)

class User_rolle_exportCSVTest(TestCase):
	# User / Rolle / AF : Das wird mal die Hauptseite für
	# Aktualisierungen / Ergänzungen / Löschungen von Rollen und Verbindungen
	def setUp(self):
		Anmeldung(self.client.login)
		Setup_database()
		TblOrga.objects.create (
			team = 'Django-Team-01',
			themeneigentuemer = 'Ihmchen_01',
		)

		TblOrga.objects.create (
			team = 'Django-Team-02',
			themeneigentuemer = 'Ihmchen_02',
		)

		TblAfliste.objects.create (
			af_name = 			'rva_01219_beta91_job_abst',
			neu_ab = 			timezone.now(),
		)

		TblAfliste.objects.create (
			af_name = 			'rva_01219_beta91_job_abst_nicht_zugewiesen',
			neu_ab = 			timezone.now(),
		)

		# Drei User: XV und DV aktiv, AV gelöscht
		TblUserIDundName.objects.create (
			userid = 			'xv13254',
			name = 				'User_xv13254',
			orga = 				TblOrga.objects.get(team = 'Django-Team-01'),
			zi_organisation =	'AI-BA',
			geloescht = 		False,
			abteilung = 		'ZI-AI-BA',
			gruppe = 			'ZI-AI-BA-PS',
		)
		TblUserIDundName.objects.create (
			userid = 			'dv13254',
			name = 				'User_xv13254',
			orga = 				TblOrga.objects.get(team = 'Django-Team-01'),
			zi_organisation =	'AI-BA',
			geloescht = 		False,
			abteilung = 		'ZI-AI-BA',
			gruppe = 			'ZI-AI-BA-PS',
		)
		TblUserIDundName.objects.create (
			userid = 			'av13254',
			name = 				'User_xv13254',
			orga = 				TblOrga.objects.get(team = 'Django-Team-01'),
			zi_organisation =	'AI-BA',
			geloescht = 		True,
			abteilung = 		'ZI-AI-BA',
			gruppe = 			'ZI-AI-BA-PS',
		)

		# Zwei Rollen, die auf den XV-User vergeben werden
		TblRollen.objects.create (
			rollenname = 		'Erste Neue Rolle',
			system =			'Testsystem',
			rollenbeschreibung = 'Das ist eine Testrolle',
		)
		TblRollen.objects.create (
			rollenname = 		'Zweite Neue Rolle',
			system =			'Irgendein System',
			rollenbeschreibung = 'Das ist auch eine Testrolle',
		)

		# Drei AF-Zuordnungen
		TblRollehataf.objects.create (
			mussfeld =			True,
			einsatz =			TblRollehataf.EINSATZ_XABCV,
			bemerkung = 		'Irgend eine halbwegs sinnvolle Beschreibung',
			af = 				TblAfliste.objects.get(af_name = 'rva_01219_beta91_job_abst'),
			rollenname = 		TblRollen.objects.get(rollenname= 'Erste Neue Rolle'),
		)
		TblRollehataf.objects.create (
			mussfeld =			True,
			einsatz =			TblRollehataf.EINSATZ_XABCV,
			bemerkung = 		'Irgend eine halbwegs sinnvolle Beschreibung',
			af = 				TblAfliste.objects.get(af_name = 'rva_01219_beta91_job_abst_nicht_zugewiesen'),
			rollenname = 		TblRollen.objects.get(rollenname= 'Erste Neue Rolle'),
		)
		TblRollehataf.objects.create (
			mussfeld =			False,
			einsatz =			TblRollehataf.EINSATZ_XABCV,
			bemerkung = 		'Auch irgend eine halbwegs sinnvolle Beschreibung',
			af = 				TblAfliste.objects.get(af_name = 'rva_01219_beta91_job_abst'),
			rollenname = 		TblRollen.objects.get(rollenname= 'Zweite Neue Rolle'),
		)

		# Dem XV-User werden zwei Rollen zugewiesen, dem AV- und DV-User keine
		TblUserhatrolle.objects.create(
			userid =	 		TblUserIDundName.objects.get(userid = 'xv13254'),
			rollenname = 		TblRollen.objects.first(),
			schwerpunkt_vertretung = 'Schwerpunkt',
			bemerkung = 		'Das ist eine Testrolle für ZI-AI-BA-PS',
			letzte_aenderung= 	timezone.now(),
		)
		TblUserhatrolle.objects.create(
			userid =	 		TblUserIDundName.objects.get(userid = 'xv13254'),
			rollenname = 		TblRollen.objects.get(rollenname = 'Zweite Neue Rolle'),
			schwerpunkt_vertretung = 'Vertretung',
			bemerkung = 		'Das ist auch eine Testrolle für ZI-AI-BA-PS',
			letzte_aenderung= 	timezone.now(),
		)

		# Die nächsten beiden Objekte werden für tblGesamt als ForeignKey benötigt
		TblUebersichtAfGfs.objects.create(
			name_gf_neu = 		"GF-foo in tblÜbersichtAFGF",
			name_af_neu =		"AF-foo in tblÜbersichtAFGF",
			zielperson = 		'Fester BesterTester'
		)
		TblUebersichtAfGfs.objects.create(
			name_gf_neu = 		"GF-foo-gelöscht in tblÜbersichtAFGF",
			name_af_neu =		"AF-foo-gelöscht in tblÜbersichtAFGF",
			zielperson = 		'Fester BesterTester'
		)
		TblPlattform.objects.create(
			tf_technische_plattform = 'Test-Plattform'
		)

		# Getestet werden soll die Möglichkeit,
		# für einen bestimmten User festzustellen, ob er über eine definierte AF verfügt
		# und diese auch auf aktiv gesetzt ist
		TblGesamt.objects.create(
			userid_name = 		TblUserIDundName.objects.get(userid = 'xv13254'),
			tf = 				'foo-TF',
			tf_beschreibung = 	'TF-Beschreibung für foo-TF',
			enthalten_in_af = 	'Sollte die AF rva_01219_beta91_job_abst sein',
			modell =			TblUebersichtAfGfs.objects.get(name_gf_neu = "GF-foo in tblÜbersichtAFGF"),
			plattform = 		TblPlattform.objects.get(tf_technische_plattform = 'Test-Plattform'),
			gf = 				'GF-foo',
			datum = 			timezone.now(),
			geloescht = 		False,
		)

		# und hier noch ein bereits gelöschtes Recht auf TF-Ebene.
		# ToDo Noch eine komplette AF mit allen GFs als gelöscht markiert vorbereiten
		# ToDo Noch eine komplette AF mit GF und TFD in anderer Rolle vorbereiten
		TblGesamt.objects.create(
			userid_name = 		TblUserIDundName.objects.get(userid = 'xv13254'),
			tf = 				'foo-TF-gelöscht',
			tf_beschreibung = 	'TF-Beschreibung für foo-TF-gelöscht',
			enthalten_in_af = 	'Sollte die AF rva_01219_beta91_job_abst sein',
			modell =			TblUebersichtAfGfs.objects.get(name_gf_neu = "GF-foo in tblÜbersichtAFGF"),
			plattform = 		TblPlattform.objects.get(tf_technische_plattform = 'Test-Plattform'),
			gf = 				'GF-foo',
			datum = 			timezone.now() - timedelta(days=365),
			geloescht = 		True,
		)

	# Eine leere Auswahl
	def test_panel_online_without_selection(self):
		url = reverse('uhr_matrix')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "User_xv13254", 2)
		self.assertContains(response, '<a href="/rapp/user_rolle_af/matrix_csv/?"', 1)
		self.assertContains(response, '<a href="/rapp/user_rolle_af/matrix_csv/kompakt/?"', 1)
		self.assertContains(response, '<th><small>Erste Neue Rolle</small></th>', 1)
		self.assertContains(response, '<th><small>Zweite Neue Rolle</small></th>', 1)
		self.assertContains(response, 'Django-Team-01', 2)
		self.assertContains(response, 'Schwerpunkt', 1)
		self.assertContains(response, 'Vertretung', 1)

	# Eine gültige Auswahl für einen User in einer Gruppe
	def test_panel_online_with_valid_selection(self):
		url = '{0}{1}'.format(reverse('uhr_matrix'), '?name=UseR&gruppe=BA-ps')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "User_xv13254", 2)
		self.assertContains(response, '<a href="/rapp/user_rolle_af/matrix_csv/?name=UseR&gruppe=BA-ps&"', 1)
		self.assertContains(response, '<a href="/rapp/user_rolle_af/matrix_csv/kompakt/?name=UseR&gruppe=BA-ps&"', 1)
		self.assertContains(response, '<th><small>Erste Neue Rolle</small></th>', 1)
		self.assertContains(response, '<th><small>Zweite Neue Rolle</small></th>', 1)
		self.assertContains(response, 'Django-Team-01', 2)
		self.assertContains(response, 'Schwerpunkt', 1)
		self.assertContains(response, 'Vertretung', 1)

	# Eine gültige Auswahl für einen User in einer Gruppe, csv-Export Langvariante
	def test_panel_long_pdf_with_valid_selection(self):
		url = '{0}{1}'.format(reverse('uhr_matrix_csv'), '?name=UseR&gruppe=BA-ps')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Name;Erste Neue Rolle;Zweite Neue Rolle\r\n", 1)
		self.assertContains(response, "User_xv13254;Schwerpunkt;Vertretung\r\n", 1)

	# Eine gültige Auswahl für einen User in einer Gruppe, csv-Export kurzvariante
	def test_panel_short_pdf_with_valid_selection(self):
		url = '{0}{1}'.format(reverse('uhr_matrix_csv'), 'kompakt/?name=UseR&gruppe=BA-ps')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Name;Erste Neue Rolle;Zweite Neue Rolle\r\n", 1)
		self.assertContains(response, "User_xv13254;S;V\r\n", 1)

class Import_new_csv_single_record(TestCase):
	# Tests für den Import neuer CSV-Listen und der zugehörigen Tabellen
	def setUp(self):
		Anmeldung(self.client.login)
		Setup_database()
		url = reverse('import')
		self.response = self.client.get(url)

		Tblrechteneuvonimport.objects.create(
			identitaet = 			'xv13254',
			nachname = 				'Bestertester',
			vorname = 				'Fester',
			tf_name = 				'supergeheime_TF',
			tf_beschreibung = 		'Die Beschreibung der supergeheimen TF',
			af_anzeigename = 		'rva_12345_geheime_AF',
			af_beschreibung = 		'Beschreibung der Geheim-AF',
			hoechste_kritikalitaet_tf_in_af = 'k',
			tf_eigentuemer_org = 	'ZI-AI-BA',
			tf_applikation = 		'RUVDE',
			tf_kritikalitaet = 		'u',
			gf_name = 				'rvg_12345_geheime_AF',
			gf_beschreibung = 		'Beschreibung der Geheim-GF',
			direct_connect = 		False,
			af_zugewiesen_an_account_name = 'av13254',
			af_gueltig_ab = 		timezone.now() - timedelta(days=364),
			af_gueltig_bis = 		timezone.now() + timedelta(days=365),
			af_zuweisungsdatum = 	timezone.now() - timedelta(days=366),
		)
	def test_importpage_table_entry(self):
		num = Tblrechteneuvonimport.objects.filter(vorname = 'Fester').count()
		self.assertEqual(num, 1)
	def test_importpage_view_status_code(self):
		url = reverse('import')
		response = self.client.get(url)
		self.assertEqual(self.response.status_code, 200)
	def test_importpage_csrf(self):
		self.assertContains(self.response, 'csrfmiddlewaretoken')
	def test_importpage_has_cuurent_comments_active(self):
		self.assertContains(self.response, 'nicht Excel wegen Unicode!')

class Setup_database(TestCase):
	# Tests für den Import der Stored Procedures in die Datenbank
	# Tests für den Import der Stored Procedures in die Datenbank
	def setUp(self):
		Anmeldung(self.client.login)
		url = reverse('stored_procedures')
		self.response = self.client.get(url)

	def test_setup_database_view_status_code(self):
		self.assertEqual(self.response.status_code, 200)

	def test_setup_database_search_context(self):
		self.assertContains(self.response, 'Ansonsten: Finger weg, das bringt hier nichts!')

	def test_setup_database_csrf(self):
		self.assertContains(self.response, 'csrfmiddlewaretoken')

	def test_setup_setup_database_load_stored_proc(self):
		url = reverse('stored_procedures')
		data = {}
		self.response = self.client.post(url, data)
		self.assertContains(self.response, 'anzahl_import_elemente war erfolgreich.', 2)
		self.assertContains(self.response, 'call_anzahl_import_elemente war erfolgreich.', 1)
		self.assertContains(self.response, 'vorbereitung war erfolgreich.', 1)
		self.assertContains(self.response, 'neueUser war erfolgreich.', 1)
		self.assertContains(self.response, 'behandleUser war erfolgreich.', 1)
		self.assertContains(self.response, 'behandleRechte war erfolgreich.', 1)
		self.assertContains(self.response, 'loescheDoppelteRechte war erfolgreich.', 1)
		self.assertContains(self.response, 'setzeNichtAIFlag war erfolgreich.', 1)
		self.assertContains(self.response, 'erzeuge_af_liste war erfolgreich.', 1)
		self.assertContains(self.response, 'ueberschreibeModelle war erfolgreich.', 1)

class Import_new_csv_single_record(TestCase):
	# Tests für den Import neuer CSV-Listen und der zugehörigen Tabellen
	def setUp(self):
		Anmeldung(self.client.login)
		Setup_database()
		url = reverse('import')
		self.response = self.client.get(url)
		# Lösche alle Einträge in der Importtabelle
		Tblrechteneuvonimport.objects.all().delete()

		# Zunächst: Behandeln eines einzelnen Records
		Tblrechteneuvonimport.objects.create(
			identitaet = 			'Test_xv13254',
			nachname = 				'Bestertester',
			vorname = 				'Fester',
			tf_name = 				'supergeheime_TF',
			tf_beschreibung = 		'Die Beschreibung der supergeheimen TF',
			af_anzeigename = 		'rva_12345_geheime_AF',
			af_beschreibung = 		'Beschreibung der Geheim-AF',
			hoechste_kritikalitaet_tf_in_af = 'k',
			tf_eigentuemer_org = 	'ZI-AI-BA',
			tf_applikation = 		'RUVDE',
			tf_kritikalitaet = 		'u',
			gf_name = 				'rvg_12345_geheime_AF',
			gf_beschreibung = 		'Beschreibung der Geheim-GF',
			direct_connect = 		False,
			af_zugewiesen_an_account_name = 'Test_av13254',
			af_gueltig_ab = 		timezone.now() - timedelta(days=364),
			af_gueltig_bis = 		timezone.now() + timedelta(days=365),
			af_zuweisungsdatum = 	timezone.now() - timedelta(days=366),
		)

	def test_importpage_view_status_code(self):
		self.assertEqual(self.response.status_code, 200)

	def test_importpage_csrf(self):
		self.assertContains(self.response, 'csrfmiddlewaretoken')

	# hier wird nur ein einzelner Datensatz in die Importtabelle übernommen.
	# Im späteren Testverlauf wird die Tabelle wieder gelöscht.
	def test_importpage_table_entry(self):
		num = Tblrechteneuvonimport.objects.filter(vorname = 'Fester').count()
		self.assertEqual(num, 1)

class Import_new_csv_files_no_input(TestCase):
	# Und nun Test des Imports dreier Dateien.
	# Die erste Datei erstellt zwei User mit Rechten
	# Die zweite Datei fügt einen User hinzu, ändert einen zweiten und löscht einen dritten
	# Datei 3 löscht alle User und deren Rechte für die Organisation wieder.
	def setUp(self):
		Anmeldung(self.client.login)
		Setup_database()
		url = reverse('import')
		self.response = self.client.post(url, {})

	def test_import_no_input_correct_page(self):
		self.assertContains(self.response, 'Auswahl der Organisation und Hochladen der Datei')

	def test_import_no_input_correct_following_page(self):
		# Wir landen wieder auf derselben Seite
		self.assertEqual(self.response.status_code, 200)
		self.assertContains(self.response, 'Auswahl der Organisation und Hochladen der Datei')

	def test_import_no_input_form_error(self):
		# Es muss ein Formfehler erkannt werden
		form = self.response.context.get('form')
		self.assertTrue(form.errors)

class Import_new_csv_files_wrong_input(TestCase):
	# Und nun Test des Imports dreier Dateien.
	# Die erste Datei erstellt zwei User mit Rechten
	# Die zweite Datei fügt einen User hinzu, ändert einen zweiten und löscht einen dritten
	# Datei 3 löscht alle User und deren Rechte für die Organisation wieder.
	def setUp(self):
		Anmeldung(self.client.login)
		Setup_database()
		data = {
			'organisation': 'foo blabla',
		}
		url = reverse('import')
		self.response = self.client.post(url, data)

	def test_import_wrong_input_correct_page(self):
		self.assertContains(self.response, 'Auswahl der Organisation und Hochladen der Datei')

	def test_import_wrong_input_correct_following_page(self):
		# Wir landen wieder auf derselben Seite
		self.assertEqual(self.response.status_code, 200)
		self.assertContains(self.response, 'Auswahl der Organisation und Hochladen der Datei')

	def test_import_wrong_input_form_error(self):
		# Es muss ein Formfehler erkannt werden
		form = self.response.context.get('form')
		self.assertTrue(form.errors)

class Import_helper_functions(TestCase):
	def test_import_datum_konverter(self):
		datum = patch_datum('07.03.2019')
		self.assertEqual(datum, '2019-03-07 00:00+0100')

	def test_import_datum_konverter_leereingabe(self):
		datum = patch_datum('')
		self.assertEqual(datum, None)

	def test_import_neuer_import(self):
		# Neuer Aufruf sollte keinen Fehler liefern
		(flag, imp) = neuer_import(None)
		self.assertFalse(flag)
