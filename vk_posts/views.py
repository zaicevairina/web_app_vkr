from django.shortcuts import render
from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from vk_worker import upload_post_from_vk_group, show_all_groups, delete_row_group_from_user_library, update_post_from_vk_group, show_user_library, search_in_user_vk_library
from env import credentials,project_id,private_key

@login_required
@csrf_exempt
def search_page(request):
	if request.method == 'GET':
		return render(request, 'vk_search.html', {'title': 'Добавить группу'})
	elif request.method == 'POST':
		# pritn(request.POST)
		data = upload_post_from_vk_group(request.user.username, request.POST.get('search'),project_id,credentials)
		if data == []:
			return render(request, 'vk_search.html', {'title': 'Добавить', 'msg': 'Такой группы не существует'})	
		return render(request, 'success.html', {'msg': 'Успех'})
	else:
		HttpResponseNotAllowed(['GET', 'POST'])

@login_required
@csrf_exempt
def user_posts(request):
	if request.method == 'GET':
		data = show_all_groups(request.user.username,project_id,credentials)
		print(data)
		return render(request, 'user_posts.html', {'data': data})
	elif request.method == 'POST':
		data = show_all_groups(request.user.username,project_id,credentials)
		if request.POST.get('delete'):
			id = request.POST.get('delete')
			delete_row_group_from_user_library(request.user.username ,id , project_id=project_id, credentials=credentials)
			for i in data:
				if i[0] == id:
					data.remove(i)
					break
			return render(request, 'user_posts.html', {'data': data, 'msg': f'Группа удалена'})
		elif request.POST.get('update'):
			id = request.POST.get('update')
			update_post_from_vk_group(request.user.username,id , project_id, credentials=credentials)
			return render(request, 'user_posts.html', {'data': data, 'msg': f'Группа обновлена'})
	else:
		HttpResponseNotAllowed(['GET', 'POST'])

