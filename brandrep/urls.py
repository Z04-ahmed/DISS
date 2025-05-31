from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='brandrep_signup'),
    path('login/', views.login_view, name='brandrep_login'),
    path('dashboard/', views.dashboard, name='brand_dashboard'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/manage/', views.manage_products, name='manage_products'),
    path('products/<int:product_id>/view/', views.view_product, name='view_product'),
    path('products/<int:product_id>/edit/', views.edit_product, name='edit_product'),
    path('products/<int:product_id>/delete/', views.delete_product, name='delete_product'),
] 