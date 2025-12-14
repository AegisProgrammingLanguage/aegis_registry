from django.urls import path
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('packages/', views.PackageListView.as_view(), name='package_list'),
    path('packages/<str:name>/', views.PackageDetailView.as_view(), name='package_detail'),
]
