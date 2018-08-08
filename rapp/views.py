# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Create your views here.

from django.shortcuts import get_object_or_404
from rapp.models import TblUserIDundName, TblGesamt, TblOrga, TblPlattform
from django.views import generic, View

from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
#from .filters import UserFilter

# Imports für die Selektions-Views panel, slektion u.a.
from django.contrib.auth.models import User
from django.shortcuts import render
from .filters import PanelFilter
from django.core.paginator import Paginator

from .forms import BastelForm

# Zum Einlesen der csv
import tablib
from tablib import Dataset
from import_export import resources
from .ressources import MyCSVImporterModel
from .models import Tblrechteneuvonimport


###################################################################
# Die Einstiegsseite
class IndexView(View):
	def get(self, request):

		# Zeige ein paar Statistik-Infos über die RechteDB.
		# Das stellt sicher, dass die Anbidnung an die Datenbank funzt
		num_rights = TblGesamt.objects.all().count()
		num_userids = TblUserIDundName.objects.all().count
		num_active_userids = TblUserIDundName.objects.filter(geloescht=False).count
		num_plattforms = TblPlattform.objects.count
		num_iamba = TblGesamt.objects.filter(geloescht=False,
											 	userid_name__abteilung__icontains='ZI-AI-BA', userid_name__geloescht = False).count
		num_userids_in_department = TblUserIDundName.objects.filter(geloescht=False, abteilung__icontains='ZI-AI-BA').count
		num_teams = TblOrga.objects.all().count
		num_active_rights = TblGesamt.objects.filter(geloescht=False).count

		return HttpResponse(
			render(
				request,
				'index.html',
				context = {
					'num_rights': num_rights,
					'num_active_rights': num_active_rights,
					'num_userIDs': num_userids,
					'num_iam_ba': num_iamba,
					'num_activeUserIDs': num_active_userids,
					'num_plattforms': num_plattforms,
					'num_userIDsInDepartment': num_userids_in_department,
					'num_teams': num_teams,
					'num_users': User.objects.all().count,
				},
			)
		)



###################################################################
# Die Gesamtliste der Rechte ungefiltert
class GesamtListView(generic.ListView):
	model = TblGesamt
	paginate_by = 100

# Die Detailsicht eines einzelnen Rechts
class GesamtDetailView(generic.DetailView):
	model = TblGesamt


###################################################################
# Die Gesamtliste der User ungefiltert
class UserIDundNameListView(generic.ListView):
	model = TblUserIDundName
	paginate_by = 100

# Die Detailsicht eines einzelnen Users
# class UserIDundNameDetailView(generic.DetailView):
#	model = TblUserIDundName


from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

class TblUserIDundNameCreate(CreateView):
	model = TblUserIDundName
	fields = '__all__'
	initial = {'geloscht' : 'False',}

class TblUserIDundNameUpdate(UpdateView):
	model = TblUserIDundName
	fields = '__all__'

class TblUserIDundNameDelete(DeleteView):
	model = TblUserIDundName
	success_url = reverse_lazy('userliste')

def userToggleGeloescht(request, pk):
	# View function zum Togglen des Gelöscht-Flags in der DB für eine konkrete Instanz.
	# Dieser Aufruf wird nicht in zwei Schritten als GET / POST-Kombination durchgeführt.
	# sondern ausschließlich als GET.
	user_inst = get_object_or_404(TblUserIDundName, pk = pk)

	user_inst.geloescht = not user_inst.geloescht
	user_inst.save()

	# redirect to a new URL:
	return HttpResponseRedirect(reverse('userliste') )

###################################################################
# Die Gesamtliste der Teams (TblOrga)

class TeamListView(generic.ListView):
	model = TblOrga
	# paginate_by = 100

class TblOrgaCreate(CreateView):
	model = TblOrga
	fields = '__all__'
	initial = {'geloscht' : 'False',}

class TblOrgaUpdate(UpdateView):
	model = TblOrga
	fields = '__all__'

class TblOrgaDelete(DeleteView):
	model = TblOrga
	success_url = reverse_lazy('teamliste')

###################################################################
# Die Ab hier kommen die Views für das Panel

"""
###################################################################
# Nur zum Zeigen, wie das mit den Panels gehen könnte....

def search(request):
	user_list = User.objects.all()
	user_filter = UserFilter(request.GET, queryset=user_list)
	return render(request, 'rapp/user_list.html', {'filter': user_filter})
"""

###################################################################
# Panel geht direkt auf die Gesamt Datentabelle

def panel(request):
	panel_list = TblGesamt.objects.all()
	panel_filter = PanelFilter(request.GET, queryset=panel_list)
	panel_list = panel_filter.qs

	pagesize = request.GET.get('pagesize')

	if type(pagesize) == type(None) or int(pagesize) < 1:
		pagesize = 20
	else:
		pagesize = int(pagesize)

	paginator = Paginator(panel_list, pagesize)
	page = request.GET.get('page', 1)
	try:
		pages = paginator.page(page)
	except PageNotAnInteger:
		pages = paginator.page(1)
	except EmptyPage:
		pages = paginator.page(paginator.num_pages)

	args = {'paginator': paginator, 'filter': panel_filter, 'pages': pages, 'meineTabelle': panel_list, 'pagesize': pagesize}
	return render(request, 'rapp/panel_list.html', args)


###################################################################
# neueListe dient dem Einlesen einer neuen csv-Datei


def xneueListe(request):

	if request.method == 'POST':
		myCSVImporterModel = MyCSVImporterModel()
		dataset = Dataset()
		csv_tabelle_von_extern = request.FILES['myfile']

		imported_data = dataset.load(csv_tabelle_von_extern.read().decode('utf-8'), format='csv')
		result = myCSVImporterModel.import_data(dataset, dry_run=True)  # Test the data import

		if not result.has_errors():
			myCSVImporterModel.import_data(dataset, dry_run=False)  # Actually import now

	return render(request, 'rapp/importcsv.html')

def neueListe(request):
	data = {}
	if "GET" == request.method:
		return render(request, "rapp/importcsv.html", data)
	# if not GET, then proceed
	try:
		csv_file = request.FILES["csv_file"]

		if not csv_file.name.endswith('.csv'):
			message.error(request, 'File is not CSV type')
			return HttpResponseRedirect(reverse("neueliste"))
		# if file is too large, return
		if csv_file.multiple_chunks():
			message.error(request, "Uploaded file is too big (%.2f MB)." % (csv_file.size / (1024 * 1024),))
			return HttpResponseRedirect(reverse("neueliste"))

		file_data = csv_file.read().decode("utf-8")

		lines = file_data.split("\n")
		# loop over the lines and save them in db. If error , store as string and then display
		for line in lines:
			if line != "":
				fields = line.split(";")
				data_dict = {}
				data_dict["Identität"] = fields[0]
				data_dict["Nachname"] = fields[1]
				data_dict["Vorname"] = fields[2]
				try:
					form = BastelForm(data_dict)
					if form.is_valid():
						form.save()
					else:
						print("neueListe: Form is invalid, %s")
						messages.error(request, 'Form is invalid.').error(form.errors.as_json())
				except Exception as e:
					print("neueListe: Irgendwas mit der Form klappt nicht")
					#messages.error("error_logger").error(repr(e))
					pass
		messages.info(request, 'Datei wurde eingelesen.')
		print("es wurden insgesamt %d Daten verarbeitet,", lines.count)

	except Exception as e:
		print('äh, da geht was nicht')
	#	logging.getLogger("error_logger").error("Unable to upload file. " + repr(e))
	#	messages.error(request, "Unable to upload file. " + repr(e))

	return HttpResponseRedirect(reverse("neueliste"))

