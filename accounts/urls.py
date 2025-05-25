from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.home_view, name='home'),
    path('wishlist/', views.favourite_products_view, name='favourites'),
path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.update_profile_view, name='edit_profile'),
path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
path('record-view/<int:product_id>/', views.record_view, name='record_view'),
]
