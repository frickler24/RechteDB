"""
Some Ressources for handling csv and Excel sheets

"""

from import_export import resources
from .models import Tblrechteneuvonimport

class MyCSVImporterModel(resources.ModelResource):
	class Meta:
		delimiter = ";"
		model = Tblrechteneuvonimport
		encoding = "utf8mb4"

