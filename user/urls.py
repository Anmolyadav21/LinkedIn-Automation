from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login', views.login, name='login'),  # Login page (handles '/')
    path('', views.signup_view, name='signup'),  # Login page (handles '/')
    path('dashboard/', views.dashboard, name='dashboard'),# Dashboard page
    path('logout/', views.logout_view, name='logout'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
