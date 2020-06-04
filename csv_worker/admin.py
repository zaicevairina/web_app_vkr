from django.contrib import admin
from csv_worker.models import CSV

class CSVAdmin(admin.ModelAdmin):
	  list_display = ('user', 'csv_file')

# Register your models here.

admin.site.register(CSV, CSVAdmin)
# Register your models here.
