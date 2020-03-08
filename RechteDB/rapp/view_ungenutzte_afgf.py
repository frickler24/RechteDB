import sys

from django.shortcuts import render
from django.db import connection

def panel_ungenutzte_afgf(request):
    """
    Zeige die Liste ungenutzter Rollen;
    Eine Rolle ist dann ungenutzt, wenn kein Element aus UserHatRolle einen Verweis auf den Rollennamen hat.
    :param request: wird Ignoriert
    :return: Gerendertes HTML
    """

    if request.method != 'GET':
        return HttpResponse("Fehlerhafter Aufruf in panel_unusedTeamList")

    antwort, fehler = hole_daten()
    return render(
        request, 'rapp/ungenutzte_afgf.html', context={
            'teams': antwort,
            'fehler': fehler,
        },
    )


def hole_daten():
    """
    Ausführen der Stored Procedure ungenutzteAFGF
    :return: Das Antwort-Array und gegebenenfalls Fehlerinformationen
    """
    antwort = {}
    fehler = None

    with connection.cursor() as cursor:
        try:
            cursor.callproc ("ungenutzteAFGF")
            tmp = cursor.fetchall()
            for line in tmp:
                antwort[line[0]] = line[1]
        except:
            e = sys.exc_info()[0]
            fehler = 'Error in panel_unusedTeamList: {}'.format(e)
            print(fehler)
    cursor.close()
    return antwort, fehler
