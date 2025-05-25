from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('<int:pk>/', views.product_detail, name='product_detail'),
    path('create/', views.create_product, name='create_product'),
    path('brand-rep/signup/', views.brand_rep_signup, name='brand_rep_signup'),
    path('brand-rep/login/', views.brand_rep_login, name='brand_rep_login'),

    # Dashboard
    path('dashboard/', views.brand_dashboard, name='brand_dashboard'),
    path('products/add/', views.add_product, name='add_product'),
]
