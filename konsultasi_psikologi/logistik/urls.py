from django.urls import path
from . import views

urlpatterns = [
    # Inventori
    path('inventori/', views.inventori_list, name='inventori_list'),
    path('inventori/tambah/', views.inventori_tambah, name='inventori_tambah'),
    path('inventori/edit/<int:pk>/', views.inventori_edit, name='inventori_edit'),
    path('inventori/hapus/<int:pk>/', views.inventori_hapus, name='inventori_hapus'),

    # Cabang
    path('cabang/', views.cabang_list, name='cabang_list'),
    path('cabang/tambah/', views.cabang_tambah, name='cabang_tambah'),
    path('cabang/edit/<int:pk>/', views.cabang_edit, name='cabang_edit'),
    path('cabang/hapus/<int:pk>/', views.cabang_hapus, name='cabang_hapus'),

    # Supplier
    path('supplier/', views.supplier_list, name='supplier_list'),
    path('supplier/tambah/', views.supplier_tambah, name='supplier_tambah'),
    path('supplier/edit/<int:pk>/', views.supplier_edit, name='supplier_edit'),
    path('supplier/hapus/<int:pk>/', views.supplier_hapus, name='supplier_hapus'),

    # Barang Masuk
    path('barang_masuk/', views.barangmasuk_list, name='barangmasuk_list'),
    path('barangmasuk/tambah/', views.barangmasuk_tambah, name='barangmasuk_tambah'),
]
