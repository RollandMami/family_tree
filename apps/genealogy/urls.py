from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
	path('arbre/', views.tree_view, name='tree_view'),
	path('arbre/details/<int:person_id>/', views.person_details_ajax, name='person_details_ajax'),
]