import sys

from django.shortcuts import render

from .forms import FormUmbenennen
from .models import TblRollen
from .stored_procedures import connection


def panel_rolle_umbenennen(request):
    """
    Zeige das Formular zum Umbenennen von Rollen
    :param request: GET oder POST Request vom Browser
    :return: Gerendertes HTML
    """
    meldung = list()
    fehlermeldung = list()

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = FormUmbenennen(request.POST)
        # check whether it's valid:
        if form.is_valid():
            alter_name = form.cleaned_data['alter_name']
            neuer_name = form.cleaned_data['neuer_name']
            # print(alter_name, neuer_name)

            # Schau nach, ob der alte Name existiert und der neue Name nicht existiert
            altok = TblRollen.objects.filter(rollenname=alter_name).count() == 1
            neuok = TblRollen.objects.filter(rollenname=neuer_name).count() == 0

            if not neuok or not altok:
                if not altok:
                    fehlermeldung.append("Der bestehende Rollenname '{}' existiert nicht.".format(alter_name))
                if not neuok:
                    fehlermeldung.append("Der neue Rollenname '{}' existiert bereits.".format(neuer_name))
            else:
                with connection.cursor() as cursor:
                    try:
                        cursor.callproc("rolle_umbenennen", [alter_name, neuer_name])
                        meldung.append('Prozedur ausgeführt')
                    except:
                        e = sys.exc_info()[0]
                        fehlermeldung.append('Error in Rollen_umbenennen: {}'.format(e))
                        print(e)
                        print(sys.exc_info())
                    cursor.close()

                # Schau nach, ob nun der alte Name nicht mehr existiert und der neue Name existiert
                altok = TblRollen.objects.filter(rollenname=alter_name).count() == 0
                neuok = TblRollen.objects.filter(rollenname=neuer_name).count() == 1

                if not neuok or not altok:
                    if not altok:
                        fehlermeldung\
                            .append("Der bestehende Rollenname '{}' existiert immer noch."
                                    .format(alter_name))
                    if not neuok:
                        fehlermeldung\
                            .append("Der neue Rollenname '{}' existiert nach Umbenennen doch nicht."
                                    .format(neuer_name))
                else:
                    meldung.append('Habe folgende Umbenennung durchgeführt:')

    # GET (or any other method)
    else:
        form = FormUmbenennen()

    return render(
        request,
        'rapp/rolle_umbenennen.html',
        context={
            'form': form,
            'meldung': meldung,
            'fehlermeldung': fehlermeldung,
        },
    )