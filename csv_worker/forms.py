from django import forms
from csv_worker.models import CSV

class CsvForm(forms.ModelForm):

	class Meta:
		model = CSV
		fields = ('csv_file',)
