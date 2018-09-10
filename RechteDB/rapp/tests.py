
# Create your tests here.

from django.urls import reverse, resolve
from django.test import TestCase
from .views import home, GesamtDetailView

from .models import TblOrga, TblUebersichtAfGfs, TblUserIDundName, TblPlattform, TblGesamt, \
	TblAfliste, TblUserhatrolle, TblRollehataf, TblRollen

from datetime import datetime, timedelta
from django.utils import timezone

# Sind die einzelnen Hsuptseiten erreichbar?
class HomeTests(TestCase):
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

	def test_adminrapp_l12_view_status_code(self):
		url = reverse('home')[:-5] + 'adminrapp/tblracfgruppen'
		response = self.client.get(url)
		self.assertEquals(response.status_code, 301)

	def test_adminrapp_l13_view_status_code(self):
		url = reverse('home')[:-5] + 'adminrapp/tblafliste'
		response = self.client.get(url)
		self.assertEquals(response.status_code, 301)

	def test_adminrapp_l14_view_status_code(self):
		url = reverse('home')[:-5] + 'adminrapp/tblgesamthistorie'
		response = self.client.get(url)
		self.assertEquals(response.status_code, 301)

	def test_adminrapp_l15_view_status_code(self):
		url = reverse('home')[:-5] + 'adminrapp/tblrechteneuvonimport'
		response = self.client.get(url)
		self.assertEquals(response.status_code, 301)

# Funktioniert die Gesamtliste?
class GesamtlisteTests(TestCase):
	def setUp(self):
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
		print (url)
		response = self.client.get(url)
		self.assertEquals(response.status_code, 200)

"""
	def test_gesamtliste_url_resolves_view(self):
		url= reverse('gesamt-detail', kwargs={'pk': TblGesamt.objects.get(tf = 'Die superlange schnuckelige TF').id})
		view = resolve(url)
		self.assertEquals(view.func, GesamtListView.as_view)
"""

# Geht die Team-Liste?
class TeamListTests(TestCase):
	# Ist die Seite da?
	# ToDo: Beim Test der Teamliste fehlen noch die drei subpanels. Aber evtl. fällt die gesamte Liste weg
	def test_teamlist_view_status_code(self):
		url = reverse('teamliste')
		response = self.client.get(url)
		self.assertEquals(response.status_code, 200)
class CreateTeamTests(TestCase):
	def setUp(self):
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


# Geht die User-Liste?
class UserListTests(TestCase):
	# Ist die Seite da?
	# ToDo: Beim Test der Userliste fehlen noch die drei subpanels. Aber evtl. fällt die gesamte Liste weg
	def test_userlist_view_status_code(self):
		url = reverse('userliste')
		response = self.client.get(url)
		self.assertEquals(response.status_code, 200)
class CreateUserTests(TestCase):
	def setUp(self):
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

	"""
	def test_create_user_url_resolves_new_topic_view(self):
		view = resolve('/userliste/create/')
		self.assertEquals(view.func, TblOrgaCreate.as_view)

	"""

	def test_create_user_view_contains_link_back_to_board_topics_view(self):
		new_user_url = reverse('user-create')
		userlist_url = reverse('userliste')
		response = self.client.get(new_user_url)
		self.assertContains(response, 'href="{0}"'.format(userlist_url))


# Suche-/Filterpanel. Das wird mal die Hauptseite für Reports
class PanelTests(TestCase):
	def setUp(self):
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


# User / Rolle / AF : Das wird mal die Hauptseite für Aktualisierungen * Ergänzungen / Löschungen von Rollen und Verbindungen
class user_rolle_afTests(TestCase):
	def setUp(self):
		TblOrga.objects.create (
			team = 'Django-Team-01',
			themeneigentuemer = 'Ihmchen_01',
		)

		TblAfliste.objects.create (
			af_name = 			'rva_01219_beta91_job_abst',
			neu_ab = 			timezone.now(),
		)

		TblUserIDundName.objects.create (
			userid = 			'xv10099',
			name = 				'User_xv10099',
			orga = 				TblOrga.objects.get(team = 'Django-Team-01'),
			zi_organisation =	'AI-BA',
			geloescht = 		False,
			abteilung = 		'ZI-AI-BA',
			gruppe = 			'ZI-AI-BA-PS',
		)

		TblRollen.objects.create (
			rollenname = 		'Erste Neue Rolle',
			system =			'Testsystem',
			rollenbeschreibung = 'Das ist eine Testrolle für das Gesamtsystem',
			datum =				timezone.now(),
		)

		TblRollehataf.objects.create (
			mussfeld =			True,
			einsatz =			2, # EINSATZ_XABCV aus models.py
			bemerkung = 		'Irgend eine halbwegs sinnvolle Beschreibung',
			af = 				TblAfliste.objects.get(af_name = 'rva_01219_beta91_job_abst'),
			rollenname = 		TblRollen.objects.get(rollenname= 'Erste Neue Rolle'),

		)

		TblUserhatrolle.objects.create (
			userid = 			TblUserIDundName.objects.get(userid = 'xv10099'),
			# rollenname = 		TblRollen.objects.get(rollenname = 'Erste Neue Rolle'),
			rollenname = 		TblRollen.objects.first(),
			schwerpunkt_vertretung = 'Schwerpunkt',
			bemerkung = 		'Das ist eine Testrolle für ZI-AI-BA-PS',
			letzte_aenderung= 	timezone.now(),
		)

	# Ist die Seite da?
	def test_panel_view_status_code(self):
		url = reverse('user_rolle_af')
		response = self.client.get(url)
		self.assertEquals(response.status_code, 200)
	def test_panel_view_with_valid_selection_status_code(self):
		url = '{0}{1}'.format(reverse('user_rolle_af'), '?geloescht=3&userid_name__zi_organisation=ai-ba')
		response = self.client.get(url)
		self.assertEquals(response.status_code, 200)
		self.assertContains(response, "User_xv10099")
	def test_panel_view_with_invalid_selection_status_code(self):
		url = '{0}{1}'.format(reverse('user_rolle_af'), '?geloescht=99&zi_organisation=ZZ-XX')
		response = self.client.get(url)
		self.assertEquals(response.status_code, 200)
		self.assertContains(response, "Keine Treffer")
	def test_panel_view_with_invalid_selection_returns_complete_list_status_code(self):
		url = '{0}{1}'.format(reverse('user_rolle_af'), '?DAS_FELD_GIBTS_NICHT=1')
		response = self.client.get(url)
		self.assertEquals(response.status_code, 200)
		self.assertContains(response, "User_xv10099")
	def test_panel_view_contains_link_back_to_home_view(self):
		new_user_url = reverse('user_rolle_af')
		userlist_url = reverse('home')
		response = self.client.get(new_user_url)
		self.assertContains(response, 'href="{0}"'.format(userlist_url))

