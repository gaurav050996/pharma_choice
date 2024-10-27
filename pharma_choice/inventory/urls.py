from django.urls import path
from . import views

urlpatterns = [
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('drugs/', views.DrugListView.as_view(), name='drug_list'),
    path('order/<int:drug_id>/', views.order_drug, name='order_drug'),
    path('order-success/', views.order_success, name='order_success'),
    path('edit-drug/<int:drug_id>/', views.edit_drug, name='edit_drug'),
    path('delete-drug/<int:drug_id>/', views.delete_drug, name='delete_drug'),
    path('add-drug/', views.add_drug, name='add_drug'),
    path('add-category/', views.add_category, name='add_category'),
]