from django.urls import path
from . import views

urlpatterns = [
    path('resep/', views.resep_list, name='resep_list'),
    path('resep/add/', views.resep_add, name='resep_add'),
    path('resep/<int:pk>/edit/', views.resep_edit, name='resep_edit'),
    path('resep/item/<int:pk_item>/delete/', views.resep_item_delete, name='resep_item_delete'),

    path('order/from_resep/<int:resep_id>/', views.order_from_resep, name='order_from_resep'),
    path('order/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/', views.order_list, name='order_list'),
]
