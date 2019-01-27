from django.urls import reverse, resolve
from django.test import TestCase
from ..views import home

from ..models import TblOrga, TblUebersichtAfGfs, TblUserIDundName, TblPlattform, TblGesamt, \
	TblAfliste, TblUserhatrolle, TblRollehataf, TblRollen, Tblrechteneuvonimport

from datetime import datetime, timedelta
from django.utils import timezone
# from django.core.files.base import ContentFile
import re
from ..anmeldung import Anmeldung


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
		self.assertEquals(response.status_code, 200)

	def test_home_url_resolves_home_view(self):
		view = resolve('/rapp/')
		self.assertEquals(view.func, home)


	# Erreichbarkeit der Admin-Seiten (Simpel-Modus)
	def test_adminrapp_view_status_code(self):
		url = reverse('home')[:-5] + 'adminrapp'
		response = self.client.get(url)
		self.assertEquals(response.status_code, 301)

	def test_adminrapp_l1_view_status_code(self):
		url = reverse('home')[:-5] + 'adminrapp/tbluserhatrolle'
		response = self.client.get(url)
		self.assertEquals(response.status_code, 301)

	def test_adminrapp_l2_view_status_code(self):
		url = reverse('home')[:-5] + 'adminrapp/tblrollehataf'
		response = self.client.get(url)
		self.assertEquals(response.status_code, 301)

	def test_adminrapp_l3_view_status_code(self):
		url = reverse('home')[:-5] + 'adminrapp/tblrollen'
		response = self.client.get(url)
		self.assertEquals(response.status_code, 301)

	def test_adminrapp_l4_view_status_code(self):
		url = reverse('home')[:-5] + 'adminrapp/tbluebersichtafgfs'
		response = self.client.get(url)
		self.assertEquals(response.status_code, 301)

	def test_adminrapp_l5_view_status_code(self):
		url = reverse('home')[:-5] + 'adminrapp/tbluseridundname'
		response = self.client.get(url)
		self.assertEquals(response.status_code, 301)

	def test_adminrapp_l6_view_status_code(self):
		url = reverse('home')[:-5] + 'adminrapp/tblorga'
		response = self.client.get(url)
		self.assertEquals(response.status_code, 301)

	def test_adminrapp_l7_view_status_code(self):
		url = reverse('home')[:-5] + 'adminrapp/tblplattform'
		response = self.client.get(url)
		self.assertEquals(response.status_code, 301)

	def test_adminrapp_l8_view_status_code(self):
		url = reverse('home')[:-5] + 'adminrapp/tblgesamt'
		response = self.client.get(url)
		self.assertEquals(response.status_code, 301)

	def test_adminrapp_l9_view_status_code(self):
		url = reverse('home')[:-5] + 'adminrapp/tblsubsysteme'
		response = self.client.get(url)
		self.assertEquals(response.status_code, 301)

	def test_adminrapp_l10_view_status_code(self):
		url = reverse('home')[:-5] + 'adminrapp/tblsachgebiete'
		response = self.client.get(url)
		self.assertEquals(response.status_code, 301)

	def test_adminrapp_l11_view_status_code(self):
		url = reverse('home')[:-5] + 'adminrapp/tbldb2'
		response = self.client.get(url)
		self.assertEquals(response.status_code, 301)

	""" Diese Admin-Seite ist derzeit nicht aktiv
	def test_adminrapp_l12_view_status_code(self):
		url = reverse('home')[:-5] + 'adminrapp/tblracfgruppen'
		response = self.client.get(url)
		self.assertEquals(response.status_code, 301)
	"""

	def test_adminrapp_l13_view_status_code(self):
		url = reverse('home')[:-5] + 'adminrapp/tblafliste'
		response = self.client.get(url)
		self.assertEquals(response.status_code, 301)

	def test_adminrapp_l14_view_status_code(self):
		url = reverse('home')[:-5] + 'adminrapp/tblgesamthistorie'
		response = self.client.get(url)
		self.assertEquals(response.status_code, 301)


	def test_adminrapp_l15_view_status_code(self):
		url = reverse('home')[:-5] + 'adminrapp/racf_rechte'
		response = self.client.get(url)
		self.assertEquals(response.status_code, 301)


	def test_adminrapp_l16_view_status_code(self):
		url = reverse('home')[:-5] + 'adminrapp/orga_details'
		response = self.client.get(url)
		self.assertEquals(response.status_code, 301)


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
		self.assertEquals(response.status_code, 200)

	def test_gesamtliste_view_not_found_status_code(self):
		url = reverse('gesamt-detail', kwargs={'pk': 99999999})
		response = self.client.get(url)
		self.assertEquals(response.status_code, 404)

	# Kann das zweite Element direkt adressiert werden?
	def test_gesamtliste_view_success_status_code(self):
		url = reverse('gesamt-detail', kwargs={'pk': TblGesamt.objects.get(tf = 'Die superlange schnuckelige TF2').id})
		response = self.client.get(url)
		self.assertEquals(response.status_code, 200)

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
		self.assertEquals(response.status_code, 200)
class CreateTeamTests(TestCase):
	# Geht die Team-Liste inhaltlich?
	def setUp(self):
		Anmeldung(self.client.login)
		Setup_database()
		TblOrga.objects.create(team='MeinTeam', themeneigentuemer='Icke')

	def test_create_team_view_success_status_code(self):
		url = reverse('team-create')
		response = self.client.get(url)
		self.assertEquals(response.status_code, 200)
	"""
	def test_create_team_url_resolves_new_topic_view(self):
		view = resolve('/teamliste/create/')
		self.assertEquals(view.func, TblOrgaCreate.as_view)
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
		self.assertEquals(response.status_code, 200)
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
		self.assertEquals(response.status_code, 200)

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
		self.assertEquals(response.status_code, 200)

	def test_panel_view_with_valid_selection_status_code(self):
		url = '{0}{1}'.format(reverse('panel'), '?geloescht=3&userid_name__zi_organisation=ai-ba')
		response = self.client.get(url)
		self.assertEquals(response.status_code, 200)
		self.assertContains(response, "User_xv10099")

	def test_panel_view_with_invalid_selection1_status_code(self):
		url = '{0}{1}'.format(reverse('panel'), '?geloescht=99&userid_name__zi_organisation=ZZ-XX')
		response = self.client.get(url)
		self.assertEquals(response.status_code, 200)
		self.assertContains(response, "Keine Treffer")

	def test_panel_view_with_invalid_selection2_status_code(self):
		url = '{0}{1}'.format(reverse('panel'), '?DAS_FELD_GIBTS_NICHT=1')
		response = self.client.get(url)
		self.assertEquals(response.status_code, 200)
		self.assertContains(response, "User_xv10099")

class User_rolle_afTests(TestCase):
	# User / Rolle / AF : Das wird mal die Hauptseite für
	# Aktualisierungen / Ergänzungen / Löschungen von Rollen und Verbindungen
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

		TblUserIDundName.objects.create (
			userid = 			'xv13254',
			name = 				'User_xv13254',
			orga = 				TblOrga.objects.get(team = 'Django-Team-01'),
			zi_organisation =	'AI-BA',
			geloescht = 		False,
			abteilung = 		'ZI-AI-BA',
			gruppe = 			'ZI-AI-BA-PS',
		)

		TblRollen.objects.create (
			rollenname = 		'Erste Neue Rolle',
			system =			'Testsystem',
			rollenbeschreibung = 'Das ist eine Testrolle',
		)

		TblRollehataf.objects.create (
			mussfeld =			True,
			einsatz =			TblRollehataf.EINSATZ_XABCV,
			bemerkung = 		'Irgend eine halbwegs sinnvolle Beschreibung',
			af = 				TblAfliste.objects.get(af_name = 'rva_01219_beta91_job_abst'),
			rollenname = 		TblRollen.objects.get(rollenname= 'Erste Neue Rolle'),
		)

		TblUserhatrolle.objects.create(
			userid =	 		TblUserIDundName.objects.get(userid = 'xv13254'),
			rollenname = 		TblRollen.objects.first(),
			schwerpunkt_vertretung = 'Schwerpunkt',
			bemerkung = 		'Das ist eine Testrolle für ZI-AI-BA-PS',
			letzte_aenderung= 	timezone.now(),

		)

		# Die nächsten beiden Objekte werden wür tblGesamt als ForeignKey benötigt
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
		self.assertEquals(response.status_code, 200)
	def test_panel_view_with_valid_selection_status_code(self):
		url = '{0}{1}'.format(reverse('user_rolle_af'), '?name=UseR&gruppe=BA-ps')
		response = self.client.get(url)
		self.assertEquals(response.status_code, 200)
		self.assertContains(response, "xv13254")
	def test_panel_view_with_invalid_selection_status_code(self):
		url = '{0}{1}'.format(reverse('user_rolle_af'), '?geloescht=99&zi_organisation=ZZ-XX')
		response = self.client.get(url)
		self.assertEquals(response.status_code, 200)
		self.assertContains(response, "Keine Treffer")
	def test_panel_view_with_invalid_selection_returns_complete_list_status_code(self):
		url = '{0}{1}'.format(reverse('user_rolle_af'), '?DAS_FELD_GIBTS_NICHT=1')
		response = self.client.get(url)
		self.assertEquals(response.status_code, 200)
		self.assertContains(response, "User_xv13254")
	def test_panel_view_contains_link_back_to_home_view(self):
		new_user_url = reverse('user_rolle_af')
		userlist_url = reverse('home')
		response = self.client.get(new_user_url)
		self.assertContains(response, 'href="{0}"'.format(userlist_url))


	# Suche nach dem User und ob seiner UserID mindestens eine Rolle zugeodnet ist.
	# Falls ja, suche weiter nach der Liste der AFen zu der Rolle (Auszug).
	# Im Detail: Wir suchen über /.../user_rolle_af/<Nummer des Eintrags UserHatRolle>
	# nach dem konkreten Eintrag (die Nummer variiert über die Anzahl der ausgeführten Testfälle,
	# deshalb das etwas umständliche Gesuche unten).
	def test_panel_view_with_valid_selection_find_UserHatRolle_id(self):
		url = '{0}{1}'.format(reverse('user_rolle_af'), '?name=&orga=1&gruppe=&pagesize=100')
		response = self.client.get(url)
		self.assertEquals(response.status_code, 200)
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
		self.assertEquals(response.status_code, 200)

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
				self.assertEquals(response.status_code, 200)
			else:
				self.assertFalse(True)	# Das war nix - offensichtlich die URL nicht korrekt
		self.assertContains(response, 'Erste Neue Rolle') # Rollenname
		self.assertContains(response, 'Testsystem') # System
		self.assertContains(response, 'Das ist eine Testrolle') # Beschreibung in TblRollen
		self.assertContains(response, 'rva_01219_beta91_job_abst') # Die gesuchte AF eine Stufe tiefer
		self.assertContains(response, 'Das ist eine Testrolle für ZI-AI-BA-PS') # Beschreibung in TblUserHatRolle
		self.assertContains(response, 'Schwerpunkt') # Wertigkeit in der Verantwortungsmatrix


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
		self.assertEquals(num, 1)

	def test_importpage_view_status_code(self):
		url = reverse('import')
		response = self.client.get(url)
		self.assertEquals(self.response.status_code, 200)

	def test_importpage_csrf(self):
		self.assertContains(self.response, 'csrfmiddlewaretoken')


class Setup_database(TestCase):
	# Tests für den Import der Stored Procedures in die Datenbank
	# Tests für den Import der Stored Procedures in die Datenbank
	def setUp(self):
		Anmeldung(self.client.login)
		url = reverse('stored_procedures')
		self.response = self.client.get(url)

	def test_setup_database_view_status_code(self):
		self.assertEquals(self.response.status_code, 200)

	def test_setup_database_search_context(self):
		self.assertContains(self.response, 'Ansonsten: Finger weg, das bringt hier nichts!')


	def test_setup_database_csrf(self):
		self.assertContains(self.response, 'csrfmiddlewaretoken')

	def test_setup_setup_database_load_stored_proc(self):
		url = reverse('stored_procedures')
		data = {}
		self.response = self.client.post(url, data)
		self.assertContains(self.response, 'anzahl_import_elemente war erfolgreich.')
		self.assertContains(self.response, 'call_anzahl_import_elemente war erfolgreich.')
		self.assertContains(self.response, 'vorbereitung war erfolgreich.')
		self.assertContains(self.response, 'neueUser war erfolgreich.')
		self.assertContains(self.response, 'behandleUser war erfolgreich.')
		self.assertContains(self.response, 'behandleRechte war erfolgreich.')
		self.assertContains(self.response, 'loescheDoppelteRechte war erfolgreich.')
		self.assertContains(self.response, 'setzeNichtAIFlag war erfolgreich.')


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
		self.assertEquals(self.response.status_code, 200)

	def test_importpage_csrf(self):
		self.assertContains(self.response, 'csrfmiddlewaretoken')

	# hier wird nur ein einzelner Datensatz in die Importtabelle übernommen.
	# Im späteren Testverlauf wird die Tabelle wieder gelöscht.
	def test_importpage_table_entry(self):
		num = Tblrechteneuvonimport.objects.filter(vorname = 'Fester').count()
		self.assertEquals(num, 1)

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

	def test_import_no_imput_correct_page(self):
		self.assertContains(self.response, 'Auswahl der Organisation und Hochladen der Datei')

	def test_import_no_imput_correct_following_page(self):
		# Wir landen wieder auf derselben Seite
		self.assertEquals(self.response.status_code, 200)
		self.assertContains(self.response, 'Auswahl der Organisation und Hochladen der Datei')

	def test_import_no_imput_form_error(self):
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

	def test_import_wrong_imput_correct_page(self):
		self.assertContains(self.response, 'Auswahl der Organisation und Hochladen der Datei')

	def test_import_wrong_imput_correct_following_page(self):
		# Wir landen wieder auf derselben Seite
		self.assertEquals(self.response.status_code, 200)
		self.assertContains(self.response, 'Auswahl der Organisation und Hochladen der Datei')

	def test_import_wrong_imput_form_error(self):
		# Es muss ein Formfehler erkannt werden
		form = self.response.context.get('form')
		self.assertTrue(form.errors)

class Concept_Pages(TestCase):
	pass

