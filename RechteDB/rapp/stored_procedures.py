# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# In dieser Datei sollen die Quellen der Stored-Procedures liegen, die zum DBMS deploed werden

from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.views import generic, View

from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

from django.contrib.auth.models import User

from django.urls import reverse_lazy

def push_sp_test():
	sp = """CREATE PROCEDURE test123(test_foo varchar(255))
		BEGIN
			SELECT * FROM `tblRechteNeuVonImport` ORDER BY `TF Name`, `Identität`
		END"""


def handle_stored_procedures(request):
	# Behandle den Import von Stored-Procedures in die Datenbank
	return render(request, 'rapp/stored_procedures.html', {})

