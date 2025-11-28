"""
URL configuration for konsultasi_psikologi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import path, include
from views import dashboard


from django.contrib import admin
from django.urls import path, include
# Pastikan kamu mengimport view login dan dashboard dari pasien.views
from pasien.views import login_view, dashboard 

urlpatterns = [
    path('admin/', admin.site.urls),

    # --- PERBAIKAN DI SINI ---
    # 1. Root URL ('') sekarang mengarah ke Login
    path('', login_view, name='login_root'), 

    # 2. Dashboard kita beri alamat khusus (misal: /dashboard/)
    #    Ini penting supaya setelah login, user dilempar ke sini
    path('dashboard/', dashboard, name='dashboard'),

    # --- INCLUDE SUBSISTEM ---
    path('logistik/', include('logistik.urls')),
    path('pasien/', include('pasien.urls')),
    path('obat/', include('obat.urls')),
    
    # ⚠️ JANGAN LUPA: Masukkan juga url konsultasi agar tidak error 404
    path('konsultasi/', include('konsultasi.urls')), 
]


