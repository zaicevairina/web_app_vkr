from django.shortcuts import render
from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from search_articles import search, search_user_library
from similar_articles import create_description, find_similar, similar_articles_from_user_library
from vk_worker import search_in_user_vk_library

@login_required
@csrf_exempt
def search_page(request):
	if request.method == 'GET':
		return render(request, 'search.html', {'title': 'Поиск'})	
	elif request.method == 'POST':
		if request.POST.get('type') == 'library':
			if not request.POST.get('choice'):
				choice = 'title'
			else:
				choice = request.POST.get('choice')
			search_data = request.POST.get('search')
			if request.POST.get('type_search') == 'users':
				data = (search_user_library(request.user.username, search_data, choice))
			else:
				data = (search(search_data, choice))
			print(data)
			return render(request, 'search_data.html', {'data': data, 'search_data': search_data})
		elif request.POST.get('type') == 'vk':
			if request.POST.get('search_type_vk' == 'users'):
				data = search_in_user_vk_library(request.user.username, request.POST.get('search'),
												 mode='post_from_group')
			else:
				data = search_in_user_vk_library(request.user.username, request.POST.get('search'))
			return render(request, 'posts_search_res.html', {'data': data})
		else:
			return render(request, 'search.html', {'title': 'Поиск'})

	else:
		HttpResponseNotAllowed(['GET', 'POST'])

@login_required
@csrf_exempt
def same_article(request):
	if request.method == 'GET':
		return render(request, 'article.html')	
	elif request.method == 'POST':
		if len(request.POST['article'].split()) < 20:
			return render(request, 'article.html', {'msg': 'Слишком короткий текст. Минимальное количество слов 20.'})
		if request.POST.get('create'):
			if request.POST.get('koef') == 'cos':
				desciption = create_description(request.POST['article'], request.POST['keyword'], request.POST['annotation'], 'cos')
			else:
				desciption = create_description(request.POST['article'], request.POST['keyword'], request.POST['annotation'])
			return render(request, 'article.html', {'article': desciption[0], 'keyword': desciption[1], 'annotation': desciption[2]})	
		elif request.POST.get('find_similiar'):
			if request.POST.get('type_search') == 'users':
				similar = similar_articles_from_user_library(request.user.username, request.POST['article'], request.POST['keyword'], request.POST['annotation'])
			else:
				similar = find_similar(request.POST['article'], request.POST['keyword'], request.POST['annotation'])
				print(similar)
			return render(request, 'article_with_data.html', {
				'article': request.POST['article'], 
				'keyword': request.POST['keyword'], 
				'annotation':request.POST['annotation'], 
				'data': similar})
		return render(request, 'article.html')
	else:
		HttpResponseNotAllowed(['GET', 'POST'])
	
