# staff/urls.py
from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('class/<int:class_id>/', views.class_detail, name='class_detail'),
    path('class/<int:class_id>/edit/', views.class_update, name='class_update'),
    path('class/<int:class_id>/students/', views.manage_students, name='manage_students'),
    path('class/<int:class_id>/subjects/', views.manage_subjects, name='manage_subjects'),
]