from django.urls import path
from . import views

urlpatterns = [
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('drugs/', views.DrugListView.as_view(), name='drug_list'),
    path('order/<int:drug_id>/', views.order_drug, name='order_drug'),
    path('order-success/', views.order_success, name='order_success'),
]