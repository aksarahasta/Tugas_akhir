from django.urls import path
from . import views

urlpatterns = [
    # AUTH
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # DASHBOARD
    path('dashboard/', views.dashboard, name='dashboard'),

    # PASIEN CRUD
    path('pasien/', views.pasien_list, name='pasien_list'),
    path('pasien/<int:pk>/', views.pasien_detail, name='pasien_detail'),
    path('pasien/<int:pk>/edit/', views.pasien_edit, name='pasien_edit'),

    # KUESIONER
    path('kuesioner/isi/', views.kuesioner_isi, name='kuesioner_isi'),
    path('kuesioner/list/', views.kuesioner_list, name='kuesioner_list'),

    # BOOKING
    path('booking/buat/', views.booking_create, name='booking_create'),

    path('booking/riwayat/', views.booking_list, name='booking_list'), # List riwayat
    path('booking/bayar/<int:booking_id>/', views.booking_pay, name='booking_pay'), # Halaman bayar
]
