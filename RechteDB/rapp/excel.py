import csv
from django.http import HttpResponse


class Excel():
    response = ''

    def __init__(self, name, ftyp="text/csv"):
        self.response = HttpResponse(content_type=ftyp)
        self.response['Content-Disposition'] = 'attachment; filename="' + name + '"'
        self.response.write(u'\ufeff'.encode('utf8'))  # BOM (optional...Excel needs it to open UTF-8 file properly)
        self.writer = csv.writer(self.response, csv.excel, delimiter='\t', quotechar='"')

    def writerow(self, content):
        self.writer.writerow(content)

    def close(self):
        self.writer = None

