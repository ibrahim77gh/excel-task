from django.urls import path
from . import views

app_name = 'calculator'

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload, name='upload'),
    path('execution/<int:execution_id>/', views.detail, name='detail'),
    path('execution/<int:execution_id>/process/', views.process, name='process'),
    path('execution/<int:execution_id>/download/input/', views.download_input, name='download_input'),
    path('execution/<int:execution_id>/download/output/', views.download_output, name='download_output'),
    path('history/', views.history, name='history'),
]
