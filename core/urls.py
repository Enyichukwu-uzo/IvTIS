# core/urls.py
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('news/<slug:slug>/', views.news_detail, name='news_detail'),
    # <slug:slug> captures the article slug from the URL
    # Example: /news/science-fair-winners-2026/
    path('news-events/', views.news_events, name='news_events'),
    path('contact/', views.contact, name='contact'),
    path('admissions/', views.admissions_overview, name='admissions'),
    path('admissions/prospectus/', views.admissions_prospectus, name='admissions_prospectus'),
    path('admissions/apply/', views.admissions_apply, name='admissions_apply'),
    path('academics/', views.academics, name='academics'),
    path('parent-hub/', views.parent_hub, name='parent_hub'),
    path('pastoral/', views.pastoral, name='pastoral'),
    path('academics/class/<int:class_id>/', views.class_detail_public, name='class_detail_public'),
]
