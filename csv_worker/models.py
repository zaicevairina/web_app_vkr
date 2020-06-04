from django.db import models
from home.models import User
class CSV(models.Model):
	user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='attachments', verbose_name="пользователь")
	csv_file = models.FileField(null=True, upload_to='media/csv.csv')
	
	class Meta:
		verbose_name = "Прикрепление"
		verbose_name_plural = "Прикрепления"
		ordering = ["user"]
