"""
Some Ressources for handling csv and Excel sheets

"""

from import_export import resources
from .models import Tblrechteneuvonimport

class MeinCSVImporterModel(resources.ModelResource):
	class Meta:
		model = Tblrechteneuvonimport
		#encoding = "utf-8"
		delimiter = ";"
		sortable_by = ['nachname', '-identitaet', ]

