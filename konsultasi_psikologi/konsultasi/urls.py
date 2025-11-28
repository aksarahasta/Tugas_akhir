from django.urls import path
from . import views

urlpatterns = [
    # Konselor
    path('konselor/', views.konselor_list, name='konselor_list'),
    path('konselor/add/', views.konselor_add, name='konselor_add'),
    path('konselor/edit/<int:pk>/', views.konselor_edit, name='konselor_edit'),
    path('konselor/delete/<int:pk>/', views.konselor_delete, name='konselor_delete'),

    # Jadwal
    path('jadwal/', views.jadwal_list, name='jadwal_list'),
    path('jadwal/add/', views.jadwal_add, name='jadwal_add'),
    path('jadwal/edit/<int:pk>/', views.jadwal_edit, name='jadwal_edit'),
    path('jadwal/delete/<int:pk>/', views.jadwal_delete, name='jadwal_delete'),

    # Sesi Konsultasi
    path('sesi/', views.sesi_list, name='sesi_list'),

    # Pembayaran
     path('pembayaran/', views.pembayaran_list, name='pembayaran_list'),
    path('pembayaran/', views.daftar_pembayaran, name='daftar_pembayaran'),
]
