
from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import UserForm, RegistrForm
from home.models import User
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from vk_worker import show_user_library, delete_row_article_from_user_library
from env import credentials,project_id

# Create your views here.
@login_required
def home(request):
	return render(request, 'home.html')

@csrf_exempt
def login1(request):
	if request.method == 'GET':
		form = UserForm()
		return render(request, 'login.html', {'form': form})	
	elif request.method == 'POST':
		# print(request.POST)
		user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
		if user is not None:
			login(request, user)
			response = JsonResponse({'data':'data'})
			return render(request, 'home.html')
		return render(request, 'login.html', {'error': "Ошибка авторизации"})
	else:
		HttpResponseNotAllowed(['GET', 'POST'])

@csrf_exempt
def registr(request):
	if request.method == 'GET':
		form = RegistrForm()
		return render(request, 'regis.html', {'form': form})	
	elif request.method == 'POST':
		form = RegistrForm(request.POST)
		if form.is_valid() and (form.cleaned_data['password'] == request.POST['password2']):
			user = User(username=form.cleaned_data['username'], first_name=form.cleaned_data['first_name'], last_name=form.cleaned_data['last_name'])
			user.set_password(form.cleaned_data['password'])
			user.save()
			login(request, user)
		else:
			print(form.errors.as_data())
			return render(request, 'regis.html', {'form': form})
		return render(request, 'home.html')
	else:
		HttpResponseNotAllowed(['GET', 'POST'])

@login_required
@csrf_exempt
def library(request):
	if request.method == 'GET':
		data = show_user_library(request.user.username,project_id,credentials=credentials)
		print(data)
		return render(request, 'user_library.html', {'data': data})
	elif request.method == 'POST':
		data = show_user_library(request.user.username,project_id,credentials=credentials)
		id = request.POST.get('author')
		print(data[int(id) - 1][0], data[int(id) - 1][1])
		data = delete_row_article_from_user_library(request.user.username, data[int(id) - 1][0], data[int(id) - 1][1],project_id,credentials)
		return render(request, 'user_library.html', {'data': data})
	else:
		HttpResponseNotAllowed(['GET', 'POST'])

