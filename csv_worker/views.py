import os
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponse, StreamingHttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from csv_worker.models import CSV
from csv_worker.forms import CsvForm
from django.conf import settings
import csv
from csv_download import upload_user_bd
import mimetypes
from similar_articles import create_description
# from django.core.servers.basehttp import FileWrapper
from wsgiref.util import FileWrapper
from similar_articles import package
ALLOWED_EXTENSIONS = set(['csv'])

def allowed_file(filename):
	return '.' in filename and \
		   filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@login_required
@csrf_exempt
def download(request):
	if request.method == 'GET':
		form = CsvForm()
		return render(request, 'download_csv.html', {'form': form})
	elif request.method == 'POST':
		arr = []
		if request.POST.get('save'):
			for i in request.POST:
				data = request.POST.getlist(i)
				print(data)
				if len(data) > 1:
					arr.append(data)
			res = upload_user_bd(arr, request.user.username)
			print(res)
			if res == -1:
				return render(request, 'success.html', {'msg': 'Ошибка при загрузке файла в бд'})
			else:
				return render(request, 'success.html', {'msg': 'Данные загружены'})

		else:
			form = CsvForm(request.POST, request.FILES)
			print((request.FILES['csv_file'].content_type))
			if form.is_valid() and (request.FILES['csv_file'].content_type == 'text/csv' or request.FILES['csv_file'].content_type == 'application/vnd.ms-excel'):
				new_csv = CSV(user=request.user, csv_file=form.cleaned_data['csv_file'])
				new_csv.save()
				new_form = CsvForm()
				print(new_csv.csv_file)	
				path = settings.BASE_DIR + '/media/' + str(new_csv.csv_file)
				with open(path) as obj:
					reader = csv.reader(obj, delimiter=";")
					data = list(reader)
				new_csv.delete()
				os.remove(path)
				return render(request, 'edit_csv.html', {'csvs': data})
			else:
				return render(request, 'download_csv.html', {'msg': 'Был получен не csv файл'})
				
			form = CsvForm()
		return render(request, 'home.html')		   
	else:
		HttpResponseNotAllowed(['GET', 'POST'])



@login_required
@csrf_exempt
def package_work(request):
	if request.method == 'GET':
		return render(request, 'package.html')	
	elif request.method == 'POST':
		arr = []
		if request.POST.get('save'):
			for i in request.POST:
				data = request.POST.getlist(i)
				if len(data) > 1:
					arr.append(data)
			upload_user_bd(arr, request.user.username)
		else:
			form = CsvForm(request.POST, request.FILES)
			print(request.FILES['csv_file'].content_type)
			if form.is_valid() and (request.FILES['csv_file'].content_type == 'text/csv' or request.FILES['csv_file'].content_type == 'application/vnd.ms-excel'):
				new_csv = CSV(user=request.user, csv_file=form.cleaned_data['csv_file'])
				new_csv.save()
				new_form = CsvForm()
				path = settings.BASE_DIR + '/media/' + str(new_csv.csv_file)
				new_path = settings.BASE_DIR + '/media/csv.csv'
				if (os.path.exists(new_path)):
					os.remove(new_path)
				os.rename(path, new_path)
				with open(new_path) as obj:
					reader = csv.reader(obj, delimiter=";")
					data = list(reader)
				# new_csv.delete()
				# os.remove(new_path)
				result_data = package(data)
				return render(request, 'package_csv.html', {'csvs': result_data})
			else:
				return render(request, 'package.html', {'msg': 'Был получен не csv файл'})
				
			form = CsvForm()
		return render(request, 'home.html')		   
	else:
		HttpResponseNotAllowed(['GET', 'POST'])

@login_required
@csrf_exempt
def give_file(request):
	if request.method == 'GET':
		content_type = 'text/csv'
		csv_path = (settings.BASE_DIR + '/media/csv.csv')
		arr = []
		for i in request.GET:
			data = request.GET.getlist(i)
			if len(data) > 1:
				arr.append(data)
		with open(csv_path, "w", newline="") as csv_file:
			writer = csv.writer(csv_file, delimiter=";")
			for i in arr:
				if len(i) > 1:
					writer.writerow(i)
		the_file = (settings.BASE_DIR + '/media/csv.csv')
		filename = os.path.basename(settings.BASE_DIR + '/media/csv.csv')
		chunk_size = 8192
		response = StreamingHttpResponse(FileWrapper(open(the_file, 'rb'), chunk_size),
                           content_type=mimetypes.guess_type(the_file)[0])
		response['Content-Disposition'] = "attachment; filename=%s" % filename
		response['Content-Length'] = os.path.getsize(the_file)
		return response