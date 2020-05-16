"""
    Baue eine TSV-Datei zusammenb, die zumindest in open Office udn LIbre offeice direkt importiert werden kann.
"""
import csv

from django.http import HttpResponse


class Excel():
    """
    Baue eine TSV-Datei zusammenb, die zumindest in open Office udn LIbre offeice direkt importiert werden kann.
    """

    def __init__(self, name: str, ftyp: str = "text/csv") -> None:
        """
        Erzeuge den Header der TSV-Datei mit den einzelnen Spaltennamen
        :param name: Name der Datei
        :param ftyp: Typ ist offiziell csv, aber getrennt wird aktuelle mit \ŧ
        """
        self.response = HttpResponse(content_type=ftyp)
        self.response['Content-Disposition'] = 'attachment; filename="' + name + '"'
        self.response.write(u'\ufeff'.encode('utf8'))  # BOM (optional...Excel needs it to open UTF-8 file properly)
        self.writer = csv.writer(self.response, csv.excel, delimiter='\t', quotechar='"')

    def writerow(self, content: str) -> None:
        """
        Schreibe genua eine Datenzeile
        :param content: Der Inhalt
        :return:
        """
        self.writer.writerow(content)

    def close(self) -> None:
        """
        Schließe die TSV-Datei
        :return:
        """
        self.writer = None
