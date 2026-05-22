# accounts/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views

from accounts.forms import LoginForm
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html', authentication_form=LoginForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='core:home'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),  # We'll build next
    path('application/<int:app_id>/', views.application_detail, name='application_detail'),
    path('application/<int:app_id>/accept/', views.accept_offer, name='accept_offer'),
    path('application/<int:app_id>/decline/', views.decline_offer, name='decline_offer'),
    path('register/staff/', views.register_staff, name='register_staff'),
]
from django.contrib.auth import views as auth_views

urlpatterns += [
    path('password-reset/',
         auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'),
         name='password_reset_complete'),
path('profile/', views.user_profile, name='user_profile'),
path('profile/delete/', views.delete_account, name='delete_account'),
]