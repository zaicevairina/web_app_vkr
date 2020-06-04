from csv_worker.views import download, package_work, give_file
from django.urls import path

urlpatterns = [
    path('download/', download, name='download'),
    path('package/', package_work, name='package'),
    path('give-file/', give_file, name='give_file'),

]