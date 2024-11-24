from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.DrugListView.as_view(), name='drug_list'),  # Default path
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('drugs/', views.DrugListView.as_view(), name='drug_list'),
    path('order/<int:drug_id>/', views.order_drug, name='order_drug'),
    path('order-success/', views.order_success, name='order_success'),
    path('edit-drug/<int:drug_id>/', views.edit_drug, name='edit_drug'),
    path('delete-drug/<int:drug_id>/', views.delete_drug, name='delete_drug'),
    path('add-drug/', views.add_drug, name='add_drug'),
    path('add-category/', views.add_category, name='add_category'),
    path('add-to-cart/<int:drug_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('order-history/', views.order_history, name='order_history'),
    path('login/', auth_views.LoginView.as_view(template_name='inventory/login.html'), name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
path('dashboard_redirect/', views.dashboard_redirect, name='dashboard_redirect'),  # Redirect based on role
]